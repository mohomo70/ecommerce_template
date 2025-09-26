from rest_framework import serializers
from decimal import Decimal
from .models import Order, OrderItem, OrderDraft
from catalog.serializers import ProductVariantSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem model."""
    
    variant = ProductVariantSerializer(read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'variant', 'quantity', 'price', 'line_total'
        ]
        read_only_fields = ['id', 'line_total']


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order model."""
    
    items = OrderItemSerializer(many=True, read_only=True)
    billing_full_name = serializers.ReadOnlyField()
    shipping_full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'email',
            'billing_first_name', 'billing_last_name', 'billing_company',
            'billing_address_1', 'billing_address_2', 'billing_city',
            'billing_state', 'billing_postal_code', 'billing_country', 'billing_phone',
            'shipping_first_name', 'shipping_last_name', 'shipping_company',
            'shipping_address_1', 'shipping_address_2', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country', 'shipping_phone',
            'status', 'subtotal', 'tax_amount', 'shipping_amount', 'total',
            'payment_intent_id', 'payment_method', 'payment_status',
            'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at',
            'items', 'billing_full_name', 'shipping_full_name'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'status', 'subtotal', 'tax_amount',
            'shipping_amount', 'total', 'payment_intent_id', 'payment_method',
            'payment_status', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at'
        ]


class OrderDraftSerializer(serializers.ModelSerializer):
    """Serializer for OrderDraft model."""
    
    class Meta:
        model = OrderDraft
        fields = [
            'id', 'email', 'billing_first_name', 'billing_last_name', 'billing_company',
            'billing_address_1', 'billing_address_2', 'billing_city',
            'billing_state', 'billing_postal_code', 'billing_country', 'billing_phone',
            'shipping_first_name', 'shipping_last_name', 'shipping_company',
            'shipping_address_1', 'shipping_address_2', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country', 'shipping_phone',
            'subtotal', 'tax_amount', 'shipping_amount', 'total',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'subtotal', 'tax_amount', 'shipping_amount', 'total', 'created_at', 'updated_at']
    
    def validate_email(self, value):
        """Validate email format."""
        if value and '@' not in value:
            raise serializers.ValidationError('Enter a valid email address.')
        return value
    
    def validate_billing_postal_code(self, value):
        """Validate postal code format."""
        if value and len(value) < 3:
            raise serializers.ValidationError('Enter a valid postal code.')
        return value
    
    def validate_shipping_postal_code(self, value):
        """Validate postal code format."""
        if value and len(value) < 3:
            raise serializers.ValidationError('Enter a valid postal code.')
        return value


class OrderDraftCreateSerializer(serializers.Serializer):
    """Serializer for creating order draft from cart."""
    
    def create(self, validated_data):
        """Create order draft from user's cart."""
        user = self.context['request'].user
        cart = self.context['cart']
        
        # Create or update draft
        draft, created = OrderDraft.objects.get_or_create(
            user=user,
            cart=cart,
            defaults={'email': user.email}
        )
        
        # Calculate totals
        draft.calculate_totals()
        
        return draft


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating order from draft."""
    
    draft_id = serializers.IntegerField()
    
    def validate_draft_id(self, value):
        """Validate draft exists and belongs to user."""
        try:
            draft = OrderDraft.objects.get(id=value, user=self.context['request'].user)
            if not draft.is_complete():
                raise serializers.ValidationError('Order draft is incomplete.')
            return value
        except OrderDraft.DoesNotExist:
            raise serializers.ValidationError('Order draft not found.')
    
    def create(self, validated_data):
        """Create order from draft."""
        from django.db import transaction
        
        draft = OrderDraft.objects.get(id=validated_data['draft_id'])
        
        with transaction.atomic():
            # Create order
            order = Order.objects.create(
                user=draft.user,
                email=draft.email,
                billing_first_name=draft.billing_first_name,
                billing_last_name=draft.billing_last_name,
                billing_company=draft.billing_company,
                billing_address_1=draft.billing_address_1,
                billing_address_2=draft.billing_address_2,
                billing_city=draft.billing_city,
                billing_state=draft.billing_state,
                billing_postal_code=draft.billing_postal_code,
                billing_country=draft.billing_country,
                billing_phone=draft.billing_phone,
                shipping_first_name=draft.shipping_first_name,
                shipping_last_name=draft.shipping_last_name,
                shipping_company=draft.shipping_company,
                shipping_address_1=draft.shipping_address_1,
                shipping_address_2=draft.shipping_address_2,
                shipping_city=draft.shipping_city,
                shipping_state=draft.shipping_state,
                shipping_postal_code=draft.shipping_postal_code,
                shipping_country=draft.shipping_country,
                shipping_phone=draft.shipping_phone,
                subtotal=draft.subtotal,
                tax_amount=draft.tax_amount,
                shipping_amount=draft.shipping_amount,
                total=draft.total,
                status='awaiting_payment'
            )
            
            # Create order items from cart
            for cart_item in draft.cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    variant=cart_item.variant,
                    quantity=cart_item.quantity,
                    price=cart_item.variant.price
                )
            
            # Clear cart
            draft.cart.items.all().delete()
            
            # Delete draft
            draft.delete()
            
            return order
