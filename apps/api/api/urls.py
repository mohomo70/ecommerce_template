"""
URL configuration for api project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def healthz(request):
    """Health check endpoint."""
    return JsonResponse({'status': 'ok', 'service': 'ecommerce-api'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/healthz/', healthz, name='healthz'),
    path('api/', include('rest_framework.urls')),
]
