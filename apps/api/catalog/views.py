from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, F, Count
from django.utils import timezone
from django.db import connection
from .models import Category, Product, ProductVariant
from .serializers import CategorySerializer, ProductListSerializer, ProductDetailSerializer
from .filters import ProductFilter


class CategoryListView(generics.ListAPIView):
    """List all active categories."""
    
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    pagination_class = None


class ProductListView(generics.ListAPIView):
    """List products with filtering, searching, and pagination."""
    
    queryset = Product.objects.select_related('category').prefetch_related(
        'images', 'variants'
    ).filter(is_active=True)
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'short_description']
    ordering_fields = ['name', 'created_at', 'price_range']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Add search vector filtering if search query exists
        search_query = self.request.query_params.get('search')
        if search_query:
            queryset = queryset.filter(search_vector__icontains=search_query)
        
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve a single product by slug."""
    
    queryset = Product.objects.select_related('category').prefetch_related(
        'images', 'variants'
    ).filter(is_active=True)
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'


@api_view(['GET'])
def performance_metrics(request):
    """Get database performance metrics."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT query, mean_time FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10")
        queries = cursor.fetchall()
    
    return Response({
        'slowest_queries': [
            {'query': query[0], 'mean_time': query[1]} 
            for query in queries
        ]
    })


class ProductSearchView(generics.ListAPIView):
    """Advanced product search with full-text search."""
    
    queryset = Product.objects.select_related('category').prefetch_related(
        'images', 'variants'
    ).filter(is_active=True)
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.query_params.get('q')
        
        if search_query:
            # Use PostgreSQL full-text search
            queryset = queryset.filter(search_vector__icontains=search_query)
        
        return queryset