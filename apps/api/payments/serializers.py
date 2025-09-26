from rest_framework import serializers
from .models import PaymentIntent, Payment, WebhookEvent


class PaymentIntentSerializer(serializers.ModelSerializer):
    """Serializer for PaymentIntent model."""
    
    class Meta:
        model = PaymentIntent
        fields = [
            'id', 'stripe_payment_intent_id', 'stripe_client_secret',
            'amount', 'currency', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model."""
    
    class Meta:
        model = Payment
        fields = [
            'id', 'stripe_payment_intent_id', 'stripe_charge_id',
            'amount', 'currency', 'status', 'payment_method',
            'payment_method_details', 'created_at', 'paid_at'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at']


class CreatePaymentIntentSerializer(serializers.Serializer):
    """Serializer for creating payment intent."""
    
    order_id = serializers.IntegerField()
    
    def validate_order_id(self, value):
        """Validate order exists and belongs to user."""
        from orders.models import Order
        try:
            order = Order.objects.get(id=value, user=self.context['request'].user)
            if order.status != 'awaiting_payment':
                raise serializers.ValidationError('Order is not awaiting payment.')
            return value
        except Order.DoesNotExist:
            raise serializers.ValidationError('Order not found.')
    
    def create(self, validated_data):
        """Create payment intent."""
        from orders.models import Order
        import stripe
        from django.conf import settings
        
        order = Order.objects.get(id=validated_data['order_id'])
        
        # Create Stripe payment intent
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total * 100),  # Convert to cents
            currency=order.currency or 'usd',
            metadata={
                'order_id': order.id,
                'order_number': order.order_number,
            },
            idempotency_key=validated_data.get('idempotency_key'),
        )
        
        # Create PaymentIntent record
        payment_intent_obj = PaymentIntent.objects.create(
            stripe_payment_intent_id=payment_intent.id,
            stripe_client_secret=payment_intent.client_secret,
            order=order,
            amount=order.total,
            currency=order.currency or 'usd',
            status=payment_intent.status,
            idempotency_key=validated_data.get('idempotency_key'),
        )
        
        return payment_intent_obj


class ConfirmPaymentSerializer(serializers.Serializer):
    """Serializer for confirming payment."""
    
    payment_intent_id = serializers.CharField(max_length=100)
    
    def validate_payment_intent_id(self, value):
        """Validate payment intent exists and belongs to user."""
        try:
            payment_intent = PaymentIntent.objects.get(
                stripe_payment_intent_id=value,
                order__user=self.context['request'].user
            )
            return value
        except PaymentIntent.DoesNotExist:
            raise serializers.ValidationError('Payment intent not found.')
    
    def create(self, validated_data):
        """Confirm payment and create Payment record."""
        import stripe
        from django.conf import settings
        from django.utils import timezone
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        # Retrieve payment intent from Stripe
        payment_intent = stripe.PaymentIntent.retrieve(validated_data['payment_intent_id'])
        
        # Get our PaymentIntent record
        payment_intent_obj = PaymentIntent.objects.get(
            stripe_payment_intent_id=validated_data['payment_intent_id']
        )
        
        # Update status
        payment_intent_obj.status = payment_intent.status
        payment_intent_obj.save()
        
        # Create Payment record if succeeded
        if payment_intent.status == 'succeeded':
            payment = Payment.objects.create(
                stripe_payment_intent_id=payment_intent.id,
                stripe_charge_id=payment_intent.latest_charge,
                order=payment_intent_obj.order,
                amount=payment_intent_obj.amount,
                currency=payment_intent_obj.currency,
                status='succeeded',
                payment_method=payment_intent.payment_method_types[0] if payment_intent.payment_method_types else 'card',
                payment_method_details=payment_intent.charges.data[0].payment_method_details if payment_intent.charges.data else {},
                paid_at=timezone.now(),
            )
            
            # Update order status
            payment_intent_obj.order.status = 'paid'
            payment_intent_obj.order.paid_at = timezone.now()
            payment_intent_obj.order.payment_intent_id = payment_intent.id
            payment_intent_obj.order.payment_method = payment.payment_method
            payment_intent_obj.order.payment_status = 'succeeded'
            payment_intent_obj.order.save()
            
            return payment
        
        return payment_intent_obj
