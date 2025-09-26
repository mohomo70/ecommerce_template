from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Order, OrderDraft
from .serializers import (
    OrderSerializer, OrderDraftSerializer, OrderDraftCreateSerializer, OrderCreateSerializer
)
from cart.models import Cart


class OrderDraftView(generics.RetrieveUpdateAPIView):
    """Get or update order draft."""
    
    serializer_class = OrderDraftSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart = get_or_create_cart(self.request)
        draft, created = OrderDraft.objects.get_or_create(
            user=self.request.user,
            cart=cart,
            defaults={'email': self.request.user.email}
        )
        if created:
            draft.calculate_totals()
        return draft


class OrderDraftCreateView(generics.CreateAPIView):
    """Create order draft from cart."""
    
    serializer_class = OrderDraftCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['cart'] = get_or_create_cart(self.request)
        return context


class OrderCreateView(generics.CreateAPIView):
    """Create order from draft."""
    
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]


class OrderListView(generics.ListAPIView):
    """List user's orders."""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class OrderDetailView(generics.RetrieveAPIView):
    """Get order details."""
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_draft(request):
    """Create or update order draft from cart."""
    cart = get_or_create_cart(request)
    
    # Create or update draft
    draft, created = OrderDraft.objects.get_or_create(
        user=request.user,
        cart=cart,
        defaults={'email': request.user.email}
    )
    
    # Calculate totals
    draft.calculate_totals()
    
    return Response({
        'draft_id': draft.id,
        'totals': {
            'subtotal': float(draft.subtotal),
            'tax_amount': float(draft.tax_amount),
            'shipping_amount': float(draft.shipping_amount),
            'total': float(draft.total),
        },
        'shipping_options': [
            {
                'id': 'standard',
                'name': 'Standard Shipping',
                'price': 10.00,
                'estimated_days': '3-5 business days'
            },
            {
                'id': 'express',
                'name': 'Express Shipping',
                'price': 20.00,
                'estimated_days': '1-2 business days'
            }
        ]
    })


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_order_draft(request, draft_id):
    """Update order draft with address information."""
    try:
        draft = OrderDraft.objects.get(id=draft_id, user=request.user)
    except OrderDraft.DoesNotExist:
        return Response({'error': 'Order draft not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update draft with provided data
    serializer = OrderDraftSerializer(draft, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        draft.calculate_totals()
        
        return Response({
            'draft_id': draft.id,
            'totals': {
                'subtotal': float(draft.subtotal),
                'tax_amount': float(draft.tax_amount),
                'shipping_amount': float(draft.shipping_amount),
                'total': float(draft.total),
            },
            'is_complete': draft.is_complete()
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def finalize_order(request):
    """Finalize order from draft."""
    draft_id = request.data.get('draft_id')
    
    if not draft_id:
        return Response({'error': 'draft_id is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        draft = OrderDraft.objects.get(id=draft_id, user=request.user)
    except OrderDraft.DoesNotExist:
        return Response({'error': 'Order draft not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if not draft.is_complete():
        return Response({'error': 'Order draft is incomplete'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check stock availability
    out_of_stock_items = []
    for cart_item in draft.cart.items.all():
        if cart_item.variant.track_inventory and cart_item.quantity > cart_item.variant.stock_quantity:
            out_of_stock_items.append({
                'variant_id': cart_item.variant.id,
                'name': cart_item.variant.display_name,
                'requested': cart_item.quantity,
                'available': cart_item.variant.stock_quantity
            })
    
    if out_of_stock_items:
        return Response({
            'error': 'Some items are out of stock',
            'out_of_stock_items': out_of_stock_items
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Create order
    serializer = OrderCreateSerializer(data={'draft_id': draft_id}, context={'request': request})
    if serializer.is_valid():
        order = serializer.save()
        return Response({
            'order_id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'total': float(order.total)
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def get_or_create_cart(request):
    """Get or create cart for user or session."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart