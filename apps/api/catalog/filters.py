import django_filters
from django.db.models import Q
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """Filter set for Product model."""
    
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.filter(is_active=True))
    category_slug = django_filters.CharFilter(field_name='category__slug')
    min_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='variants__price', lookup_expr='lte')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Product
        fields = ['category', 'category_slug', 'min_price', 'max_price', 'is_featured', 'in_stock', 'search']
    
    def filter_in_stock(self, queryset, name, value):
        """Filter products that have variants in stock."""
        if value:
            return queryset.filter(
                variants__is_active=True,
                variants__track_inventory=False
            ).union(
                queryset.filter(
                    variants__is_active=True,
                    variants__track_inventory=True,
                    variants__stock_quantity__gt=0
                )
            ).distinct()
        return queryset
    
    def filter_search(self, queryset, name, value):
        """Filter products by search query."""
        if value:
            return queryset.filter(
                Q(name__icontains=value) |
                Q(description__icontains=value) |
                Q(short_description__icontains=value) |
                Q(search_vector__icontains=value)
            )
        return queryset
