from django.urls import path
from . import views

urlpatterns = [
    path('adjustments/', views.StockAdjustmentListView.as_view(), name='stock-adjustment-list'),
    path('adjustments/<int:pk>/', views.StockAdjustmentDetailView.as_view(), name='stock-adjustment-detail'),
    path('adjustments/create/', views.create_stock_adjustment, name='create-stock-adjustment'),
    path('alerts/', views.LowStockAlertListView.as_view(), name='low-stock-alert-list'),
    path('alerts/<int:pk>/', views.LowStockAlertDetailView.as_view(), name='low-stock-alert-detail'),
    path('alerts/<int:alert_id>/acknowledge/', views.acknowledge_low_stock_alert, name='acknowledge-low-stock-alert'),
    path('reports/', views.InventoryReportListView.as_view(), name='inventory-report-list'),
    path('reports/generate/', views.generate_inventory_report, name='generate-inventory-report'),
    path('movements/', views.StockMovementListView.as_view(), name='stock-movement-list'),
    path('levels/', views.stock_levels, name='stock-levels'),
    path('valuation/', views.inventory_valuation, name='inventory-valuation'),
    path('stream/', views.inventory_stream, name='inventory-stream'),
]
