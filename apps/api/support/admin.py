from django.contrib import admin
from .models import SupportTicket, TicketMessage, FAQ, ProductReview, ReviewVote

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'subject', 'status', 'priority', 'created_at', 'updated_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['subject', 'description', 'customer__email']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(TicketMessage)
class TicketMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'ticket', 'sender', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at']
    search_fields = ['message', 'sender__email']
    readonly_fields = ['created_at']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['id', 'question', 'category', 'is_published', 'created_at']
    list_filter = ['category', 'is_published', 'created_at']
    search_fields = ['question', 'answer']

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'customer', 'rating', 'is_verified_purchase', 'created_at']
    list_filter = ['rating', 'is_verified_purchase', 'created_at']
    search_fields = ['title', 'review', 'customer__email', 'product__name']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    list_display = ['id', 'review', 'user', 'is_helpful', 'created_at']
    list_filter = ['is_helpful', 'created_at']
    search_fields = ['user__email']