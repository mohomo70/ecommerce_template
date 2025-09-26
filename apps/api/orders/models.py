from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User
from catalog.models import ProductVariant
from cart.models import Cart


class Order(models.Model):
    """Order model for completed purchases."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('awaiting_payment', 'Awaiting Payment'),
        ('paid', 'Paid'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    # Order identification
    order_number = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
    # Customer information
    email = models.EmailField()
    billing_first_name = models.CharField(max_length=100)
    billing_last_name = models.CharField(max_length=100)
    billing_company = models.CharField(max_length=100, blank=True)
    billing_address_1 = models.CharField(max_length=200)
    billing_address_2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100)
    billing_phone = models.CharField(max_length=20, blank=True)
    
    # Shipping information
    shipping_first_name = models.CharField(max_length=100)
    shipping_last_name = models.CharField(max_length=100)
    shipping_company = models.CharField(max_length=100, blank=True)
    shipping_address_1 = models.CharField(max_length=200)
    shipping_address_2 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100)
    shipping_phone = models.CharField(max_length=20, blank=True)
    
    # Order details
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    
    # Payment information
    payment_intent_id = models.CharField(max_length=100, blank=True)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=20, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['user']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Order {self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()
        super().save(*args, **kwargs)
    
    def generate_order_number(self):
        """Generate unique order number."""
        import uuid
        return f"ORD-{uuid.uuid4().hex[:8].upper()}"
    
    @property
    def billing_full_name(self):
        return f"{self.billing_first_name} {self.billing_last_name}"
    
    @property
    def shipping_full_name(self):
        return f"{self.shipping_first_name} {self.shipping_last_name}"
    
    def can_transition_to(self, new_status):
        """Check if order can transition to new status."""
        valid_transitions = {
            'draft': ['awaiting_payment', 'cancelled'],
            'awaiting_payment': ['paid', 'cancelled'],
            'paid': ['processing', 'cancelled'],
            'processing': ['shipped', 'cancelled'],
            'shipped': ['delivered'],
            'delivered': ['refunded'],
            'cancelled': [],
            'refunded': [],
        }
        return new_status in valid_transitions.get(self.status, [])


class OrderItem(models.Model):
    """Individual item in an order."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    variant = models.ForeignKey(ProductVariant, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    line_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    
    class Meta:
        ordering = ['id']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['variant']),
        ]
    
    def __str__(self):
        return f"{self.quantity}x {self.variant.display_name} in {self.order}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.price * self.quantity
        super().save(*args, **kwargs)


class OrderDraft(models.Model):
    """Draft order for checkout process."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='order_drafts')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='drafts')
    
    # Customer information (can be partial)
    email = models.EmailField(blank=True)
    billing_first_name = models.CharField(max_length=100, blank=True)
    billing_last_name = models.CharField(max_length=100, blank=True)
    billing_company = models.CharField(max_length=100, blank=True)
    billing_address_1 = models.CharField(max_length=200, blank=True)
    billing_address_2 = models.CharField(max_length=200, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_state = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)
    billing_phone = models.CharField(max_length=20, blank=True)
    
    # Shipping information
    shipping_first_name = models.CharField(max_length=100, blank=True)
    shipping_last_name = models.CharField(max_length=100, blank=True)
    shipping_company = models.CharField(max_length=100, blank=True)
    shipping_address_1 = models.CharField(max_length=200, blank=True)
    shipping_address_2 = models.CharField(max_length=200, blank=True)
    shipping_city = models.CharField(max_length=100, blank=True)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20, blank=True)
    shipping_country = models.CharField(max_length=100, blank=True)
    shipping_phone = models.CharField(max_length=20, blank=True)
    
    # Calculated totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['cart']),
        ]
    
    def __str__(self):
        return f"Draft for {self.user.email} - {self.created_at}"
    
    def calculate_totals(self):
        """Calculate order totals based on cart items."""
        self.subtotal = self.cart.subtotal
        self.tax_amount = self.cart.tax_amount
        self.shipping_amount = Decimal('10.00')  # Fixed shipping for now
        self.total = self.subtotal + self.tax_amount + self.shipping_amount
        self.save()
    
    def is_complete(self):
        """Check if draft has all required information."""
        required_fields = [
            'email', 'billing_first_name', 'billing_last_name',
            'billing_address_1', 'billing_city', 'billing_state',
            'billing_postal_code', 'billing_country',
            'shipping_first_name', 'shipping_last_name',
            'shipping_address_1', 'shipping_city', 'shipping_state',
            'shipping_postal_code', 'shipping_country'
        ]
        return all(getattr(self, field) for field in required_fields)