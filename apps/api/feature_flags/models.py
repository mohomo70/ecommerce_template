from django.db import models


class FeatureFlag(models.Model):
    """Feature flag model for controlling feature availability."""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {'Enabled' if self.is_enabled else 'Disabled'}"