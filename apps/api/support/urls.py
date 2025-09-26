from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.SupportTicketListView.as_view(), name='support-ticket-list'),
    path('tickets/<int:pk>/', views.SupportTicketDetailView.as_view(), name='support-ticket-detail'),
    path('tickets/<int:ticket_id>/messages/', views.TicketMessageCreateView.as_view(), name='ticket-message-create'),
    path('faq/', views.FAQListView.as_view(), name='faq-list'),
    path('reviews/product/<int:product_id>/', views.ProductReviewListView.as_view(), name='product-review-list'),
    path('reviews/<int:pk>/', views.ProductReviewDetailView.as_view(), name='product-review-detail'),
    path('reviews/<int:review_id>/vote/', views.vote_review, name='review-vote'),
]
