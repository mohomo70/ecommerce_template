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
    path('api/auth/', include('accounts.urls')),
    path('api/', include('catalog.urls')),
    path('api/cart/', include('cart.urls')),
    path('api/orders/', include('orders.urls')),
]
