from django.urls import path
from . import views

urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('products/', views.ProductListView.as_view(), name='product-list'),
    path('products/search/', views.ProductSearchView.as_view(), name='product-search'),
    path('products/<slug:slug>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('performance/', views.performance_metrics, name='performance-metrics'),
]
