from rest_framework import serializers
from decimal import Decimal
from .models import Cart, CartItem
from catalog.serializers import ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model."""
    
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True)
    line_total = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'variant', 'variant_id', 'quantity', 
            'line_total', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_quantity(self, value):
        """Validate quantity against stock."""
        variant_id = self.initial_data.get('variant_id')
        if variant_id:
            from catalog.models import ProductVariant
            try:
                variant = ProductVariant.objects.get(id=variant_id)
                if variant.track_inventory and value > variant.stock_quantity:
                    raise serializers.ValidationError(
                        f'Not enough stock. Available: {variant.stock_quantity}'
                    )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError('Invalid product variant')
        return value
    
    def create(self, validated_data):
        """Create or update cart item."""
        variant_id = validated_data.pop('variant_id')
        quantity = validated_data.get('quantity')
        
        # Get or create cart
        cart = self.context['cart']
        
        # Check if item already exists
        try:
            cart_item = CartItem.objects.get(cart=cart, variant_id=variant_id)
            cart_item.quantity += quantity
            cart_item.save()
            return cart_item
        except CartItem.DoesNotExist:
            validated_data['variant_id'] = variant_id
            return CartItem.objects.create(cart=cart, **validated_data)


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model."""
    
    items = CartItemSerializer(many=True, read_only=True)
    totals = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'totals', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class CartUpdateSerializer(serializers.Serializer):
    """Serializer for updating cart item quantities."""
    
    quantity = serializers.IntegerField(min_value=1)
    
    def validate_quantity(self, value):
        """Validate quantity against stock."""
        cart_item = self.context['cart_item']
        if cart_item.variant.track_inventory and value > cart_item.variant.stock_quantity:
            raise serializers.ValidationError(
                f'Not enough stock. Available: {cart_item.variant.stock_quantity}'
            )
        return value
