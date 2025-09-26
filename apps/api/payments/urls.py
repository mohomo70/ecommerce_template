from django.urls import path
from . import views

urlpatterns = [
    path('intent/create/', views.create_payment_intent, name='create-payment-intent'),
    path('intent/confirm/', views.confirm_payment, name='confirm-payment'),
    path('intent/<int:pk>/', views.PaymentIntentDetailView.as_view(), name='payment-intent-detail'),
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('webhook/', views.stripe_webhook, name='stripe-webhook'),
]
