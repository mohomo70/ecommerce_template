from django.contrib import admin
from .models import Order, OrderItem, OrderDraft


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total', 'payment_status',
        'created_at', 'paid_at'
    ]
    list_filter = ['status', 'payment_status', 'created_at', 'paid_at']
    search_fields = ['order_number', 'user__email', 'billing_first_name', 'billing_last_name']
    readonly_fields = ['order_number', 'created_at', 'updated_at', 'paid_at', 'shipped_at', 'delivered_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'created_at', 'updated_at')
        }),
        ('Billing Information', {
            'fields': (
                'billing_first_name', 'billing_last_name', 'billing_company',
                'billing_address_1', 'billing_address_2', 'billing_city',
                'billing_state', 'billing_postal_code', 'billing_country', 'billing_phone'
            )
        }),
        ('Shipping Information', {
            'fields': (
                'shipping_first_name', 'shipping_last_name', 'shipping_company',
                'shipping_address_1', 'shipping_address_2', 'shipping_city',
                'shipping_state', 'shipping_postal_code', 'shipping_country', 'shipping_phone'
            )
        }),
        ('Financial Information', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'total')
        }),
        ('Payment Information', {
            'fields': ('payment_intent_id', 'payment_method', 'payment_status')
        }),
        ('Timestamps', {
            'fields': ('paid_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'variant', 'quantity', 'price', 'line_total']
    list_filter = ['order__status', 'order__created_at']
    search_fields = ['order__order_number', 'variant__sku', 'variant__product__name']


@admin.register(OrderDraft)
class OrderDraftAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email', 'total', 'is_complete', 'created_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'billing_first_name', 'billing_last_name']
    readonly_fields = ['created_at', 'updated_at', 'subtotal', 'tax_amount', 'shipping_amount', 'total']
    
    def is_complete(self, obj):
        return obj.is_complete()
    is_complete.boolean = True
    is_complete.short_description = 'Complete'