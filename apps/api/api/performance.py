"""
Performance optimization configurations and utilities.
"""

from django.core.cache import cache
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DatabasePerformanceMiddleware:
    """Middleware to log slow database queries."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.slow_query_threshold = 0.1  # 100ms
    
    def __call__(self, request):
        # Reset query count and time
        initial_queries = len(connection.queries)
        initial_time = sum(float(q['time']) for q in connection.queries)
        
        response = self.get_response(request)
        
        # Calculate query metrics
        final_queries = len(connection.queries)
        final_time = sum(float(q['time']) for q in connection.queries)
        
        query_count = final_queries - initial_queries
        query_time = final_time - initial_time
        
        # Log slow requests
        if query_time > self.slow_query_threshold:
            logger.warning(
                f"Slow request: {request.path} - "
                f"{query_count} queries in {query_time:.3f}s"
            )
        
        return response


def cache_key_generator(view_name, *args, **kwargs):
    """Generate cache keys for API views."""
    key_parts = [view_name]
    
    # Add user ID if authenticated
    if hasattr(kwargs.get('request'), 'user') and kwargs['request'].user.is_authenticated:
        key_parts.append(f"user_{kwargs['request'].user.id}")
    
    # Add query parameters
    if hasattr(kwargs.get('request'), 'GET'):
        for key, value in sorted(kwargs['request'].GET.items()):
            key_parts.append(f"{key}_{value}")
    
    return ":".join(str(part) for part in key_parts)


def get_cache_ttl(view_name):
    """Get cache TTL for different view types."""
    ttl_map = {
        'product_list': 300,      # 5 minutes
        'product_detail': 600,    # 10 minutes
        'category_list': 1800,    # 30 minutes
        'user_profile': 60,       # 1 minute
        'cart_detail': 30,        # 30 seconds
        'order_list': 120,        # 2 minutes
    }
    return ttl_map.get(view_name, 60)  # Default 1 minute


def invalidate_related_cache(model_instance, related_models=None):
    """Invalidate cache for related models."""
    if related_models is None:
        related_models = []
    
    # Clear model-specific cache
    model_name = model_instance._meta.model_name
    cache_pattern = f"{model_name}_*"
    
    # This is a simplified version - in production, you'd use Redis SCAN
    # or maintain a cache key registry
    logger.info(f"Invalidating cache for {model_name}")


# Database optimization queries
OPTIMIZATION_QUERIES = [
    # Product catalog indexes
    "CREATE INDEX IF NOT EXISTS idx_product_name ON catalog_product (name);",
    "CREATE INDEX IF NOT EXISTS idx_product_slug ON catalog_product (slug);",
    "CREATE INDEX IF NOT EXISTS idx_product_active ON catalog_product (is_active);",
    "CREATE INDEX IF NOT EXISTS idx_product_category ON catalog_product (category_id);",
    
    # Product variant indexes
    "CREATE INDEX IF NOT EXISTS idx_variant_sku ON catalog_productvariant (sku);",
    "CREATE INDEX IF NOT EXISTS idx_variant_product ON catalog_productvariant (product_id);",
    "CREATE INDEX IF NOT EXISTS idx_variant_stock ON catalog_productvariant (stock_quantity);",
    "CREATE INDEX IF NOT EXISTS idx_variant_price ON catalog_productvariant (price);",
    
    # Order indexes
    "CREATE INDEX IF NOT EXISTS idx_order_user ON orders_order (user_id);",
    "CREATE INDEX IF NOT EXISTS idx_order_status ON orders_order (status);",
    "CREATE INDEX IF NOT EXISTS idx_order_created ON orders_order (created_at);",
    "CREATE INDEX IF NOT EXISTS idx_order_number ON orders_order (order_number);",
    
    # Cart indexes
    "CREATE INDEX IF NOT EXISTS idx_cart_user ON cart_cart (user_id);",
    "CREATE INDEX IF NOT EXISTS idx_cart_session ON cart_cart (session_key);",
    "CREATE INDEX IF NOT EXISTS idx_cart_updated ON cart_cart (updated_at);",
    
    # Inventory indexes
    "CREATE INDEX IF NOT EXISTS idx_stock_movement_variant ON inventory_stockmovement (variant_id);",
    "CREATE INDEX IF NOT EXISTS idx_stock_movement_created ON inventory_stockmovement (created_at);",
    "CREATE INDEX IF NOT EXISTS idx_stock_movement_type ON inventory_stockmovement (movement_type);",
    
    # User indexes
    "CREATE INDEX IF NOT EXISTS idx_user_email ON accounts_user (email);",
    "CREATE INDEX IF NOT EXISTS idx_user_points ON accounts_user (points);",
]


def apply_database_optimizations():
    """Apply database optimization queries."""
    with connection.cursor() as cursor:
        for query in OPTIMIZATION_QUERIES:
            try:
                cursor.execute(query)
                logger.info(f"Applied optimization: {query[:50]}...")
            except Exception as e:
                logger.error(f"Failed to apply optimization: {e}")


# Cache configuration for different data types
CACHE_CONFIGS = {
    'products': {
        'timeout': 300,  # 5 minutes
        'version': 1,
        'key_prefix': 'products',
    },
    'categories': {
        'timeout': 1800,  # 30 minutes
        'version': 1,
        'key_prefix': 'categories',
    },
    'user_sessions': {
        'timeout': 3600,  # 1 hour
        'version': 1,
        'key_prefix': 'session',
    },
    'api_responses': {
        'timeout': 60,  # 1 minute
        'version': 1,
        'key_prefix': 'api',
    },
}


def get_cache_config(cache_type):
    """Get cache configuration for a specific type."""
    return CACHE_CONFIGS.get(cache_type, {
        'timeout': 60,
        'version': 1,
        'key_prefix': 'default',
    })


# Query optimization utilities
def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """Apply common query optimizations."""
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset


def get_queryset_stats(queryset):
    """Get statistics about a queryset for debugging."""
    stats = {
        'query_count': len(connection.queries),
        'query_time': sum(float(q['time']) for q in connection.queries),
    }
    
    try:
        stats['count'] = queryset.count()
    except Exception:
        stats['count'] = 'N/A'
    
    return stats
