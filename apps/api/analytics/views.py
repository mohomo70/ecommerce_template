from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    SalesAnalytics, ProductAnalytics, CustomerAnalytics, 
    CategoryAnalytics, PageView, SearchQuery, ConversionEvent
)
from .serializers import (
    SalesAnalyticsSerializer, ProductAnalyticsSerializer, CustomerAnalyticsSerializer,
    CategoryAnalyticsSerializer, PageViewSerializer, SearchQuerySerializer,
    ConversionEventSerializer, AnalyticsSummarySerializer, TopProductSerializer,
    TopCategorySerializer, RevenueTrendSerializer
)
from catalog.models import Product, Category
from accounts.models import User
from orders.models import Order


class SalesAnalyticsListView(generics.ListAPIView):
    """List sales analytics data."""
    serializer_class = SalesAnalyticsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = SalesAnalytics.objects.all()
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset


class ProductAnalyticsListView(generics.ListAPIView):
    """List product analytics data."""
    serializer_class = ProductAnalyticsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = ProductAnalytics.objects.select_related('product')
        
        # Filter by product
        product_id = self.request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset


class CustomerAnalyticsListView(generics.ListAPIView):
    """List customer analytics data."""
    serializer_class = CustomerAnalyticsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = CustomerAnalytics.objects.select_related('customer')
        
        # Filter by customer
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset


class CategoryAnalyticsListView(generics.ListAPIView):
    """List category analytics data."""
    serializer_class = CategoryAnalyticsSerializer
    permission_classes = [IsAdminUser]
    
    def get_queryset(self):
        queryset = CategoryAnalytics.objects.select_related('category')
        
        # Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
            
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
            
        return queryset


@api_view(['GET'])
@permission_classes([IsAdminUser])
def analytics_summary(request):
    """Get analytics summary data."""
    # Get date range from query params
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Calculate summary data
    orders = Order.objects.filter(created_at__date__range=[start_date, end_date])
    
    total_revenue = orders.aggregate(total=Sum('total'))['total'] or 0
    total_orders = orders.count()
    total_customers = User.objects.filter(orders__created_at__date__range=[start_date, end_date]).distinct().count()
    total_products = Product.objects.count()
    average_order_value = orders.aggregate(avg=Avg('total'))['avg'] or 0
    
    # Calculate conversion rate (simplified)
    total_views = PageView.objects.filter(timestamp__date__range=[start_date, end_date]).count()
    conversion_rate = (total_orders / total_views * 100) if total_views > 0 else 0
    
    data = {
        'total_revenue': total_revenue,
        'total_orders': total_orders,
        'total_customers': total_customers,
        'total_products': total_products,
        'average_order_value': average_order_value,
        'conversion_rate': conversion_rate,
        'period': f"Last {days} days"
    }
    
    serializer = AnalyticsSummarySerializer(data)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def top_products(request):
    """Get top performing products."""
    days = int(request.query_params.get('days', 30))
    limit = int(request.query_params.get('limit', 10))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get top products by revenue
    products = Product.objects.annotate(
        revenue=Sum('order_items__line_total', filter=Q(order_items__order__created_at__date__range=[start_date, end_date])),
        orders=Count('order_items__order', filter=Q(order_items__order__created_at__date__range=[start_date, end_date])),
        views=Sum('analytics__views', filter=Q(analytics__date__range=[start_date, end_date]))
    ).filter(revenue__gt=0).order_by('-revenue')[:limit]
    
    data = []
    for product in products:
        conversion_rate = (product.orders / product.views * 100) if product.views and product.views > 0 else 0
        data.append({
            'product': product,
            'revenue': product.revenue or 0,
            'orders': product.orders or 0,
            'conversion_rate': conversion_rate
        })
    
    serializer = TopProductSerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def top_categories(request):
    """Get top performing categories."""
    days = int(request.query_params.get('days', 30))
    limit = int(request.query_params.get('limit', 10))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get top categories by revenue
    categories = Category.objects.annotate(
        revenue=Sum('products__order_items__line_total', filter=Q(products__order_items__order__created_at__date__range=[start_date, end_date])),
        orders=Count('products__order_items__order', filter=Q(products__order_items__order__created_at__date__range=[start_date, end_date])),
        products=Count('products', distinct=True)
    ).filter(revenue__gt=0).order_by('-revenue')[:limit]
    
    data = []
    for category in categories:
        data.append({
            'category': category,
            'revenue': category.revenue or 0,
            'orders': category.orders or 0,
            'products': category.products or 0
        })
    
    serializer = TopCategorySerializer(data, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def revenue_trend(request):
    """Get revenue trend data."""
    days = int(request.query_params.get('days', 30))
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Get daily revenue data
    daily_data = []
    current_date = start_date
    
    while current_date <= end_date:
        orders = Order.objects.filter(created_at__date=current_date)
        revenue = orders.aggregate(total=Sum('total'))['total'] or 0
        order_count = orders.count()
        
        daily_data.append({
            'date': current_date,
            'revenue': revenue,
            'orders': order_count
        })
        
        current_date += timedelta(days=1)
    
    serializer = RevenueTrendSerializer(daily_data, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_page_view(request):
    """Track a page view."""
    data = {
        'url': request.data.get('url'),
        'user': request.user.id if request.user.is_authenticated else None,
        'session_key': request.session.session_key,
        'ip_address': request.META.get('REMOTE_ADDR'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'referer': request.META.get('HTTP_REFERER'),
    }
    
    serializer = PageViewSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_search(request):
    """Track a search query."""
    data = {
        'query': request.data.get('query'),
        'user': request.user.id if request.user.is_authenticated else None,
        'results_count': request.data.get('results_count', 0),
    }
    
    serializer = SearchQuerySerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def track_conversion(request):
    """Track a conversion event."""
    data = {
        'event_type': request.data.get('event_type'),
        'user': request.user.id if request.user.is_authenticated else None,
        'session_key': request.session.session_key,
        'product': request.data.get('product_id'),
        'order': request.data.get('order_id'),
        'value': request.data.get('value'),
        'metadata': request.data.get('metadata', {}),
    }
    
    serializer = ConversionEventSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)