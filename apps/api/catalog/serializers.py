from rest_framework import serializers
from .models import Category, Product, ProductVariant, ProductImage


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model."""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'parent', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for ProductImage model."""
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'sort_order']


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for ProductVariant model."""
    
    is_in_stock = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'name', 'price', 'compare_at_price', 'cost_price',
            'stock_quantity', 'track_inventory', 'weight', 'dimensions',
            'is_active', 'is_in_stock', 'display_name'
        ]
        read_only_fields = ['id']


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Product list view (optimized for listing)."""
    
    category = CategorySerializer(read_only=True)
    primary_image = ProductImageSerializer(read_only=True)
    price_range = serializers.ReadOnlyField()
    variant_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category',
            'primary_image', 'price_range', 'is_active', 'is_featured',
            'created_at', 'variant_count'
        ]
    
    def get_variant_count(self, obj):
        return obj.variants.filter(is_active=True).count()


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for Product detail view (includes all related data)."""
    
    category = CategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    price_range = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'attributes', 'images', 'variants', 'price_range',
            'is_active', 'is_featured', 'created_at', 'updated_at'
        ]
