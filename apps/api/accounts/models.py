from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom User model with email as username and roles support."""
    
    email = models.EmailField(unique=True)
    roles = models.JSONField(default=list, help_text="List of user roles")
    
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