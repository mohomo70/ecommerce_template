from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer, CartUpdateSerializer


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


class CartView(generics.RetrieveAPIView):
    """Get current user's cart."""
    
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_or_create_cart(self.request)


class CartItemCreateView(generics.CreateAPIView):
    """Add item to cart."""
    
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['cart'] = get_or_create_cart(self.request)
        return context


class CartItemUpdateView(generics.UpdateAPIView):
    """Update cart item quantity."""
    
    serializer_class = CartUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart = get_or_create_cart(self.request)
        cart_item = get_object_or_404(
            CartItem, 
            cart=cart, 
            id=self.kwargs['item_id']
        )
        return cart_item
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['cart_item'] = self.get_object()
        return context
    
    def perform_update(self, serializer):
        """Update cart item with validation."""
        cart_item = self.get_object()
        new_quantity = serializer.validated_data['quantity']
        
        if new_quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = new_quantity
            cart_item.save()


class CartItemDeleteView(generics.DestroyAPIView):
    """Remove item from cart."""
    
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        cart = get_or_create_cart(self.request)
        return get_object_or_404(
            CartItem, 
            cart=cart, 
            id=self.kwargs['item_id']
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from cart."""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    return Response({'message': 'Cart cleared successfully'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_totals(request):
    """Get cart totals only."""
    cart = get_or_create_cart(request)
    return Response(cart.totals)