from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['line_total', 'created_at', 'updated_at']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'session_key', 'total_items', 'subtotal', 'total', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'session_key']
    inlines = [CartItemInline]
    readonly_fields = ['subtotal', 'tax_amount', 'total', 'total_items']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items__variant')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart', 'variant', 'quantity', 'line_total', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['cart__user__email', 'variant__sku', 'variant__product__name']
    readonly_fields = ['line_total', 'created_at', 'updated_at']