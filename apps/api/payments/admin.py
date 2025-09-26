from django.contrib import admin
from .models import PaymentIntent, Payment, WebhookEvent


@admin.register(PaymentIntent)
class PaymentIntentAdmin(admin.ModelAdmin):
    list_display = [
        'stripe_payment_intent_id', 'order', 'amount', 'currency', 
        'status', 'created_at'
    ]
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['stripe_payment_intent_id', 'order__order_number', 'order__user__email']
    readonly_fields = ['stripe_payment_intent_id', 'stripe_client_secret', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Stripe Information', {
            'fields': ('stripe_payment_intent_id', 'stripe_client_secret', 'idempotency_key')
        }),
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'stripe_payment_intent_id', 'order', 'amount', 'currency', 
        'status', 'payment_method', 'paid_at'
    ]
    list_filter = ['status', 'currency', 'payment_method', 'created_at', 'paid_at']
    search_fields = [
        'stripe_payment_intent_id', 'stripe_charge_id', 
        'order__order_number', 'order__user__email'
    ]
    readonly_fields = [
        'stripe_payment_intent_id', 'stripe_charge_id', 
        'created_at', 'updated_at', 'paid_at'
    ]
    
    fieldsets = (
        ('Stripe Information', {
            'fields': ('stripe_payment_intent_id', 'stripe_charge_id')
        }),
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Payment Details', {
            'fields': ('amount', 'currency', 'status', 'payment_method', 'payment_method_details')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = [
        'stripe_event_id', 'event_type', 'processed', 'created_at', 'processed_at'
    ]
    list_filter = ['event_type', 'processed', 'created_at']
    search_fields = ['stripe_event_id', 'event_type']
    readonly_fields = ['stripe_event_id', 'created_at', 'processed_at']
    
    fieldsets = (
        ('Event Information', {
            'fields': ('stripe_event_id', 'event_type', 'processed')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )