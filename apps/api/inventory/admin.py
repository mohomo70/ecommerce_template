from django.contrib import admin
from .models import StockAdjustment, LowStockAlert, InventoryReport, StockMovement


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = [
        'variant', 'adjustment_type', 'quantity', 'reason', 'user', 'created_at'
    ]
    list_filter = ['adjustment_type', 'created_at']
    search_fields = ['variant__sku', 'variant__product__name', 'reason', 'reference']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Adjustment Details', {
            'fields': ('variant', 'adjustment_type', 'quantity', 'reason', 'reference')
        }),
        ('User Information', {
            'fields': ('user', 'created_at')
        }),
    )


@admin.register(LowStockAlert)
class LowStockAlertAdmin(admin.ModelAdmin):
    list_display = [
        'variant', 'current_stock', 'threshold', 'status', 'acknowledged_by', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['variant__sku', 'variant__product__name']
    readonly_fields = ['created_at', 'acknowledged_at']
    
    fieldsets = (
        ('Alert Details', {
            'fields': ('variant', 'threshold', 'current_stock', 'status')
        }),
        ('Acknowledgment', {
            'fields': ('acknowledged_by', 'acknowledged_at', 'created_at')
        }),
    )


@admin.register(InventoryReport)
class InventoryReportAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'report_type', 'generated_by', 'generated_at'
    ]
    list_filter = ['report_type', 'generated_at']
    search_fields = ['title', 'description']
    readonly_fields = ['generated_by', 'generated_at']
    
    fieldsets = (
        ('Report Information', {
            'fields': ('report_type', 'title', 'description')
        }),
        ('Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Generation', {
            'fields': ('generated_by', 'generated_at')
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = [
        'variant', 'movement_type', 'quantity', 'reference', 'created_at'
    ]
    list_filter = ['movement_type', 'created_at']
    search_fields = ['variant__sku', 'variant__product__name', 'reference', 'notes']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Movement Details', {
            'fields': ('variant', 'movement_type', 'quantity', 'reference', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )