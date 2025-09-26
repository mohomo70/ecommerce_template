from django.contrib import admin
from .models import (
    SalesAnalytics, ProductAnalytics, CustomerAnalytics, 
    CategoryAnalytics, PageView, SearchQuery, ConversionEvent
)

@admin.register(SalesAnalytics)
class SalesAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_revenue', 'total_orders', 'total_items_sold', 'average_order_value']
    list_filter = ['date', 'created_at']
    search_fields = ['date']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date']

@admin.register(ProductAnalytics)
class ProductAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['product', 'date', 'views', 'orders', 'revenue', 'conversion_rate']
    list_filter = ['date', 'created_at']
    search_fields = ['product__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-revenue']

@admin.register(CustomerAnalytics)
class CustomerAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['customer', 'date', 'total_orders', 'total_spent', 'average_order_value', 'customer_lifetime_value']
    list_filter = ['date', 'created_at']
    search_fields = ['customer__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-total_spent']

@admin.register(CategoryAnalytics)
class CategoryAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['category', 'date', 'total_products', 'total_orders', 'total_revenue', 'average_order_value']
    list_filter = ['date', 'created_at']
    search_fields = ['category__name']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-date', '-total_revenue']

@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ['url', 'user', 'ip_address', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['url', 'user__email']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    list_display = ['query', 'user', 'results_count', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['query', 'user__email']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']

@admin.register(ConversionEvent)
class ConversionEventAdmin(admin.ModelAdmin):
    list_display = ['event_type', 'user', 'product', 'order', 'value', 'timestamp']
    list_filter = ['event_type', 'timestamp']
    search_fields = ['user__email', 'product__name']
    readonly_fields = ['timestamp']
    ordering = ['-timestamp']