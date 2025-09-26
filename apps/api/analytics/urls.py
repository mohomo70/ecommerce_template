from django.urls import path
from . import views

urlpatterns = [
    path('sales/', views.SalesAnalyticsListView.as_view(), name='sales-analytics-list'),
    path('products/', views.ProductAnalyticsListView.as_view(), name='product-analytics-list'),
    path('customers/', views.CustomerAnalyticsListView.as_view(), name='customer-analytics-list'),
    path('categories/', views.CategoryAnalyticsListView.as_view(), name='category-analytics-list'),
    path('summary/', views.analytics_summary, name='analytics-summary'),
    path('top-products/', views.top_products, name='top-products'),
    path('top-categories/', views.top_categories, name='top-categories'),
    path('revenue-trend/', views.revenue_trend, name='revenue-trend'),
    path('track/page-view/', views.track_page_view, name='track-page-view'),
    path('track/search/', views.track_search, name='track-search'),
    path('track/conversion/', views.track_conversion, name='track-conversion'),
]
