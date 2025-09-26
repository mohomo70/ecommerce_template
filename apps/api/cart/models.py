from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from catalog.models import ProductVariant
from accounts.models import User


class Cart(models.Model):
    """Shopping cart model for storing user's selected items."""
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='carts'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        if self.user:
            return f"Cart for {self.user.email}"
        return f"Cart for session {self.session_key}"
    
    @property
    def total_items(self):
        """Get total number of items in cart."""
        return sum(item.quantity for item in self.items.all())
    
    @property
    def subtotal(self):
        """Calculate subtotal before tax."""
        return sum(item.line_total for item in self.items.all())
    
    @property
    def tax_amount(self):
        """Calculate tax amount (simplified 10% tax)."""
        return self.subtotal * Decimal('0.10')
    
    @property
    def total(self):
        """Calculate total including tax."""
        return self.subtotal + self.tax_amount
    
    @property
    def totals(self):
        """Get all totals as a dictionary."""
        return {
            'subtotal': float(self.subtotal),
            'tax_amount': float(self.tax_amount),
            'total': float(self.total),
            'item_count': self.total_items,
        }


class CartItem(models.Model):
    """Individual item in a shopping cart."""
    
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        default=1
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['cart', 'variant']
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['cart']),
            models.Index(fields=['variant']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.variant.display_name} in {self.cart}"
    
    @property
    def line_total(self):
        """Calculate line total for this item."""
        return self.variant.price * self.quantity
    
    def clean(self):
        """Validate cart item."""
        from django.core.exceptions import ValidationError
        
        # Check if variant is active
        if not self.variant.is_active:
            raise ValidationError('Cannot add inactive product variant to cart')
        
        # Check stock availability
        if self.variant.track_inventory and self.quantity > self.variant.stock_quantity:
            raise ValidationError(
                f'Not enough stock. Available: {self.variant.stock_quantity}, '
                f'Requested: {self.quantity}'
            )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)