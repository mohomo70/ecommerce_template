from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """Permission class that checks if user has admin role."""
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin
        )
