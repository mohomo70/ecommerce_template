from django.urls import path
from . import views

urlpatterns = [
    path('draft/', views.OrderDraftView.as_view(), name='order-draft'),
    path('draft/create/', views.create_order_draft, name='order-draft-create'),
    path('draft/<int:draft_id>/', views.update_order_draft, name='order-draft-update'),
    path('finalize/', views.finalize_order, name='order-finalize'),
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]
