from rest_framework import serializers
from .models import (
    SalesAnalytics, ProductAnalytics, CustomerAnalytics, 
    CategoryAnalytics, PageView, SearchQuery, ConversionEvent
)
from catalog.serializers import ProductListSerializer, CategorySerializer
from accounts.serializers import UserSerializer


class SalesAnalyticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesAnalytics
        fields = [
            'id', 'date', 'total_revenue', 'total_orders', 'total_items_sold',
            'average_order_value', 'created_at', 'updated_at'
        ]


class ProductAnalyticsSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = ProductAnalytics
        fields = [
            'id', 'product', 'product_id', 'date', 'views', 'orders', 'revenue',
            'conversion_rate', 'created_at', 'updated_at'
        ]


class CustomerAnalyticsSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CustomerAnalytics
        fields = [
            'id', 'customer', 'customer_id', 'date', 'total_orders', 'total_spent',
            'average_order_value', 'last_order_date', 'customer_lifetime_value',
            'created_at', 'updated_at'
        ]


class CategoryAnalyticsSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = CategoryAnalytics
        fields = [
            'id', 'category', 'category_id', 'date', 'total_products', 'total_orders',
            'total_revenue', 'average_order_value', 'created_at', 'updated_at'
        ]


class PageViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageView
        fields = [
            'id', 'url', 'user', 'session_key', 'ip_address', 'user_agent',
            'referer', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class SearchQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = SearchQuery
        fields = ['id', 'query', 'user', 'results_count', 'timestamp']
        read_only_fields = ['timestamp']


class ConversionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversionEvent
        fields = [
            'id', 'event_type', 'user', 'session_key', 'product', 'order',
            'value', 'metadata', 'timestamp'
        ]
        read_only_fields = ['timestamp']


class AnalyticsSummarySerializer(serializers.Serializer):
    """Serializer for analytics summary data."""
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_orders = serializers.IntegerField()
    total_customers = serializers.IntegerField()
    total_products = serializers.IntegerField()
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    period = serializers.CharField()


class TopProductSerializer(serializers.Serializer):
    """Serializer for top performing products."""
    product = ProductListSerializer()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.IntegerField()
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2)


class TopCategorySerializer(serializers.Serializer):
    """Serializer for top performing categories."""
    category = CategorySerializer()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.IntegerField()
    products = serializers.IntegerField()


class RevenueTrendSerializer(serializers.Serializer):
    """Serializer for revenue trend data."""
    date = serializers.DateField()
    revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
    orders = serializers.IntegerField()
