from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartView.as_view(), name='cart-detail'),
    path('items/', views.CartItemCreateView.as_view(), name='cart-item-create'),
    path('items/<int:item_id>/', views.CartItemUpdateView.as_view(), name='cart-item-update'),
    path('items/<int:item_id>/delete/', views.CartItemDeleteView.as_view(), name='cart-item-delete'),
    path('clear/', views.clear_cart, name='cart-clear'),
    path('totals/', views.cart_totals, name='cart-totals'),
]
