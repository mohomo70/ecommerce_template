from rest_framework import serializers
from .models import SupportTicket, TicketMessage, FAQ, ProductReview, ReviewVote


class TicketMessageSerializer(serializers.ModelSerializer):
    """Serializer for TicketMessage model."""
    
    sender = serializers.StringRelatedField(read_only=True)
    
    class Meta:
        model = TicketMessage
        fields = ['id', 'sender', 'message', 'is_internal', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class SupportTicketSerializer(serializers.ModelSerializer):
    """Serializer for SupportTicket model."""
    
    customer = serializers.StringRelatedField(read_only=True)
    assigned_to = serializers.StringRelatedField(read_only=True)
    messages = TicketMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = SupportTicket
        fields = [
            'id', 'ticket_number', 'customer', 'subject', 'description',
            'category', 'priority', 'status', 'assigned_to', 'messages',
            'created_at', 'updated_at', 'resolved_at'
        ]
        read_only_fields = ['id', 'ticket_number', 'customer', 'created_at', 'updated_at', 'resolved_at']


class FAQSerializer(serializers.ModelSerializer):
    """Serializer for FAQ model."""
    
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'category', 'is_published', 'order', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProductReviewSerializer(serializers.ModelSerializer):
    """Serializer for ProductReview model."""
    
    customer = serializers.StringRelatedField(read_only=True)
    helpful_votes = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductReview
        fields = [
            'id', 'product', 'customer', 'rating', 'title', 'review',
            'is_verified_purchase', 'is_approved', 'helpful_votes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'customer', 'helpful_votes', 'created_at', 'updated_at']


class ReviewVoteSerializer(serializers.ModelSerializer):
    """Serializer for ReviewVote model."""
    
    class Meta:
        model = ReviewVote
        fields = ['id', 'review', 'user', 'is_helpful', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
