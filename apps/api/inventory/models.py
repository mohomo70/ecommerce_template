from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from catalog.models import ProductVariant
from accounts.models import User


class StockAdjustment(models.Model):
    """Model for tracking stock adjustments."""
    
    ADJUSTMENT_TYPES = [
        ('in', 'Stock In'),
        ('out', 'Stock Out'),
        ('adjustment', 'Manual Adjustment'),
        ('return', 'Return'),
        ('damage', 'Damage'),
        ('theft', 'Theft'),
    ]
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='stock_adjustments')
    adjustment_type = models.CharField(max_length=20, choices=ADJUSTMENT_TYPES)
    quantity = models.IntegerField(help_text="Positive for stock in, negative for stock out")
    reason = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True, help_text="PO number, return ID, etc.")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stock_adjustments')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant']),
            models.Index(fields=['adjustment_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_adjustment_type_display()} - {self.variant.sku} ({self.quantity:+d})"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update variant stock quantity
        self.variant.stock_quantity += self.quantity
        self.variant.save(update_fields=['stock_quantity'])


class LowStockAlert(models.Model):
    """Model for tracking low stock alerts."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
    ]
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='low_stock_alerts')
    threshold = models.PositiveIntegerField(help_text="Stock level that triggered the alert")
    current_stock = models.PositiveIntegerField(help_text="Stock level when alert was created")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    acknowledged_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='acknowledged_alerts'
    )
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Low Stock Alert - {self.variant.sku} ({self.current_stock}/{self.threshold})"
    
    def acknowledge(self, user):
        """Acknowledge the alert."""
        from django.utils import timezone
        self.status = 'acknowledged'
        self.acknowledged_by = user
        self.acknowledged_at = timezone.now()
        self.save()
    
    def resolve(self):
        """Resolve the alert."""
        self.status = 'resolved'
        self.save()


class InventoryReport(models.Model):
    """Model for storing inventory reports."""
    
    REPORT_TYPES = [
        ('stock_levels', 'Stock Levels'),
        ('movement', 'Stock Movement'),
        ('valuation', 'Inventory Valuation'),
        ('low_stock', 'Low Stock Items'),
    ]
    
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    data = models.JSONField(help_text="Report data in JSON format")
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory_reports')
    generated_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['report_type']),
            models.Index(fields=['generated_at']),
        ]
    
    def __str__(self):
        return f"{self.get_report_type_display()} - {self.title}"


class StockMovement(models.Model):
    """Model for tracking stock movements."""
    
    MOVEMENT_TYPES = [
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
        ('transfer', 'Transfer'),
        ('damage', 'Damage'),
        ('theft', 'Theft'),
    ]
    
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, related_name='stock_movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField(help_text="Positive for stock in, negative for stock out")
    reference = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['variant']),
            models.Index(fields=['movement_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_movement_type_display()} - {self.variant.sku} ({self.quantity:+d})"