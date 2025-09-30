"""
URL configuration for api project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

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
    path('api/payments/', include('payments.urls')),
    path('api/inventory/', include('inventory.urls')),
    path('api/support/', include('support.urls')),
    path('api/analytics/', include('analytics.urls')),
    path('api/', include('feature_flags.urls')),
    # OpenAPI documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
