import time
import logging
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class DatabasePerformanceMiddleware(MiddlewareMixin):
    """Middleware to log database query performance."""
    
    def process_request(self, request):
        request._db_start_time = time.time()
        request._db_queries_start = len(connection.queries)
    
    def process_response(self, request, response):
        if hasattr(request, '_db_start_time'):
            db_time = time.time() - request._db_start_time
            query_count = len(connection.queries) - getattr(request, '_db_queries_start', 0)
            
            # Add performance headers
            response['X-DB-Time'] = f"{db_time:.3f}s"
            response['X-DB-Queries'] = str(query_count)
            
            # Log slow queries
            if db_time > 0.05:  # 50ms threshold
                logger.warning(
                    f"Slow database query: {db_time:.3f}s, {query_count} queries "
                    f"for {request.path}"
                )
        
        return response
