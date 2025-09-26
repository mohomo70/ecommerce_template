from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Product, Category
from orders.models import Order, OrderItem

User = get_user_model()


class SalesAnalytics(models.Model):
    """Model for sales analytics data."""
    
    date = models.DateField()
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_items_sold = models.PositiveIntegerField(default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"Sales Analytics for {self.date}"


class ProductAnalytics(models.Model):
    """Model for product performance analytics."""
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    views = models.PositiveIntegerField(default=0)
    orders = models.PositiveIntegerField(default=0)
    revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    conversion_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['product', 'date']
        ordering = ['-date', '-revenue']
        indexes = [
            models.Index(fields=['product', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['revenue']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.product.name} on {self.date}"


class CustomerAnalytics(models.Model):
    """Model for customer analytics data."""
    
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    total_orders = models.PositiveIntegerField(default=0)
    total_spent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    last_order_date = models.DateTimeField(null=True, blank=True)
    customer_lifetime_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['customer', 'date']
        ordering = ['-date', '-total_spent']
        indexes = [
            models.Index(fields=['customer', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['total_spent']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.customer.email} on {self.date}"


class CategoryAnalytics(models.Model):
    """Model for category performance analytics."""
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField()
    total_products = models.PositiveIntegerField(default=0)
    total_orders = models.PositiveIntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    average_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['category', 'date']
        ordering = ['-date', '-total_revenue']
        indexes = [
            models.Index(fields=['category', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['total_revenue']),
        ]
    
    def __str__(self):
        return f"Analytics for {self.category.name} on {self.date}"


class PageView(models.Model):
    """Model for tracking page views."""
    
    url = models.URLField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referer = models.URLField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['url']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Page view: {self.url} at {self.timestamp}"


class SearchQuery(models.Model):
    """Model for tracking search queries."""
    
    query = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    results_count = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['query']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"Search: {self.query} ({self.results_count} results)"


class ConversionEvent(models.Model):
    """Model for tracking conversion events."""
    
    EVENT_TYPES = [
        ('page_view', 'Page View'),
        ('product_view', 'Product View'),
        ('add_to_cart', 'Add to Cart'),
        ('checkout_start', 'Checkout Start'),
        ('checkout_complete', 'Checkout Complete'),
        ('purchase', 'Purchase'),
        ('signup', 'Sign Up'),
        ('login', 'Login'),
    ]
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['event_type']),
            models.Index(fields=['user']),
            models.Index(fields=['timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} at {self.timestamp}"