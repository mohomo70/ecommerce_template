from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with email as username and roles support."""
    
    email = models.EmailField(unique=True)
    roles = models.JSONField(default=list, help_text="List of user roles")
    points = models.PositiveIntegerField(default=0, help_text="User loyalty points")
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email
    
    @property
    def is_admin(self):
        return 'admin' in self.roles
    
    @property
    def is_customer(self):
        return 'customer' in self.roles or not self.roles
    
    def add_points(self, amount, reason=""):
        """Add points to user account."""
        self.points += amount
        self.save(update_fields=['points'])
        # Log points transaction
        PointsTransaction.objects.create(
            user=self,
            amount=amount,
            reason=reason
        )
    
    def get_badge_level(self):
        """Get user's current badge level based on points."""
        if self.points >= 10000:
            return 'platinum'
        elif self.points >= 5000:
            return 'gold'
        elif self.points >= 1000:
            return 'silver'
        else:
            return 'bronze'


class PointsTransaction(models.Model):
    """Track points transactions for users."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='points_transactions')
    amount = models.IntegerField(help_text="Points amount (positive for earned, negative for spent)")
    reason = models.CharField(max_length=255, help_text="Reason for points transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.amount} points - {self.reason}"