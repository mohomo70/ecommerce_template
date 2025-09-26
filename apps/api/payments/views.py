from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.conf import settings
import stripe
import json
import logging
from .models import PaymentIntent, Payment, WebhookEvent
from .serializers import (
    PaymentIntentSerializer, PaymentSerializer, 
    CreatePaymentIntentSerializer, ConfirmPaymentSerializer
)

logger = logging.getLogger(__name__)

# Configure Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentIntentCreateView(generics.CreateAPIView):
    """Create payment intent for order."""
    
    serializer_class = CreatePaymentIntentSerializer
    permission_classes = [IsAuthenticated]


class PaymentIntentDetailView(generics.RetrieveAPIView):
    """Get payment intent details."""
    
    serializer_class = PaymentIntentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PaymentIntent.objects.filter(order__user=self.request.user)


class PaymentConfirmView(generics.CreateAPIView):
    """Confirm payment intent."""
    
    serializer_class = ConfirmPaymentSerializer
    permission_classes = [IsAuthenticated]


class PaymentListView(generics.ListAPIView):
    """List user's payments."""
    
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Payment.objects.filter(order__user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment_intent(request):
    """Create payment intent for order."""
    order_id = request.data.get('order_id')
    
    if not order_id:
        return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        from orders.models import Order
        order = Order.objects.get(id=order_id, user=request.user)
        
        if order.status != 'awaiting_payment':
            return Response(
                {'error': 'Order is not awaiting payment'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if payment intent already exists
        existing_intent = PaymentIntent.objects.filter(order=order).first()
        if existing_intent and existing_intent.status in ['requires_payment_method', 'requires_confirmation']:
            return Response({
                'client_secret': existing_intent.stripe_client_secret,
                'payment_intent_id': existing_intent.stripe_payment_intent_id,
            })
        
        # Create new payment intent
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Convert to cents
            currency='usd',
            metadata={
                'order_id': order.id,
                'order_number': order.order_number,
            },
        )
        
        # Create PaymentIntent record
        payment_intent_obj = PaymentIntent.objects.create(
            stripe_payment_intent_id=payment_intent.id,
            stripe_client_secret=payment_intent.client_secret,
            order=order,
            amount=order.total,
            currency='usd',
            status=payment_intent.status,
        )
        
        return Response({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
        })
        
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error creating payment intent: {str(e)}")
        return Response(
            {'error': 'Failed to create payment intent'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def confirm_payment(request):
    """Confirm payment intent."""
    payment_intent_id = request.data.get('payment_intent_id')
    
    if not payment_intent_id:
        return Response({'error': 'payment_intent_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Retrieve payment intent from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)
        
        # Get our PaymentIntent record
        payment_intent_obj = get_object_or_404(
            PaymentIntent,
            stripe_payment_intent_id=payment_intent_id,
            order__user=request.user
        )
        
        # Update status
        payment_intent_obj.status = payment_intent.status
        payment_intent_obj.save()
        
        if payment_intent.status == 'succeeded':
            # Create Payment record
            payment = Payment.objects.create(
                stripe_payment_intent_id=payment_intent.id,
                stripe_charge_id=payment_intent.latest_charge,
                order=payment_intent_obj.order,
                amount=payment_intent_obj.amount,
                currency=payment_intent_obj.currency,
                status='succeeded',
                payment_method='card',
                paid_at=timezone.now(),
            )
            
            # Update order status
            order = payment_intent_obj.order
            order.status = 'paid'
            order.paid_at = timezone.now()
            order.payment_intent_id = payment_intent.id
            order.payment_method = 'card'
            order.payment_status = 'succeeded'
            order.save()
            
            return Response({
                'status': 'succeeded',
                'payment_id': payment.id,
                'order_id': order.id,
                'order_number': order.order_number,
            })
        else:
            return Response({
                'status': payment_intent.status,
                'error': payment_intent.last_payment_error,
            })
            
    except PaymentIntent.DoesNotExist:
        return Response({'error': 'Payment intent not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error confirming payment: {str(e)}")
        return Response(
            {'error': 'Failed to confirm payment'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Handle Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        logger.error("Invalid payload")
        return JsonResponse({'error': 'Invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        return JsonResponse({'error': 'Invalid signature'}, status=400)
    
    # Check if event already processed
    webhook_event, created = WebhookEvent.objects.get_or_create(
        stripe_event_id=event['id'],
        defaults={
            'event_type': event['type'],
            'data': event['data'],
        }
    )
    
    if not created and webhook_event.processed:
        return JsonResponse({'status': 'already_processed'})
    
    # Process event
    try:
        if event['type'] == 'payment_intent.succeeded':
            handle_payment_intent_succeeded(event['data']['object'])
        elif event['type'] == 'payment_intent.payment_failed':
            handle_payment_intent_failed(event['data']['object'])
        elif event['type'] == 'payment_intent.canceled':
            handle_payment_intent_canceled(event['data']['object'])
        
        webhook_event.processed = True
        webhook_event.save()
        
        return JsonResponse({'status': 'success'})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return JsonResponse({'error': 'Processing failed'}, status=500)


def handle_payment_intent_succeeded(payment_intent_data):
    """Handle successful payment intent."""
    from django.utils import timezone
    
    try:
        payment_intent = PaymentIntent.objects.get(
            stripe_payment_intent_id=payment_intent_data['id']
        )
        
        # Create Payment record
        Payment.objects.create(
            stripe_payment_intent_id=payment_intent_data['id'],
            stripe_charge_id=payment_intent_data.get('latest_charge'),
            order=payment_intent.order,
            amount=payment_intent.amount,
            currency=payment_intent.currency,
            status='succeeded',
            payment_method='card',
            paid_at=timezone.now(),
        )
        
        # Update order status
        order = payment_intent.order
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.payment_intent_id = payment_intent_data['id']
        order.payment_method = 'card'
        order.payment_status = 'succeeded'
        order.save()
        
        logger.info(f"Payment succeeded for order {order.order_number}")
        
    except PaymentIntent.DoesNotExist:
        logger.error(f"PaymentIntent not found for {payment_intent_data['id']}")


def handle_payment_intent_failed(payment_intent_data):
    """Handle failed payment intent."""
    try:
        payment_intent = PaymentIntent.objects.get(
            stripe_payment_intent_id=payment_intent_data['id']
        )
        
        # Update order status
        order = payment_intent.order
        order.status = 'cancelled'
        order.payment_status = 'failed'
        order.save()
        
        logger.info(f"Payment failed for order {order.order_number}")
        
    except PaymentIntent.DoesNotExist:
        logger.error(f"PaymentIntent not found for {payment_intent_data['id']}")


def handle_payment_intent_canceled(payment_intent_data):
    """Handle canceled payment intent."""
    try:
        payment_intent = PaymentIntent.objects.get(
            stripe_payment_intent_id=payment_intent_data['id']
        )
        
        # Update order status
        order = payment_intent.order
        order.status = 'cancelled'
        order.payment_status = 'canceled'
        order.save()
        
        logger.info(f"Payment canceled for order {order.order_number}")
        
    except PaymentIntent.DoesNotExist:
        logger.error(f"PaymentIntent not found for {payment_intent_data['id']}")