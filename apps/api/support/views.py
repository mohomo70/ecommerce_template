from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import SupportTicket, TicketMessage, FAQ, ProductReview, ReviewVote
from .serializers import (
    SupportTicketSerializer, TicketMessageSerializer, FAQSerializer,
    ProductReviewSerializer, ReviewVoteSerializer
)


class SupportTicketListView(generics.ListCreateAPIView):
    """List and create support tickets."""
    
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.user).order_by('-created_at')


class SupportTicketDetailView(generics.RetrieveUpdateAPIView):
    """Get and update support ticket."""
    
    serializer_class = SupportTicketSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SupportTicket.objects.filter(customer=self.request.user)


class TicketMessageCreateView(generics.CreateAPIView):
    """Create ticket message."""
    
    serializer_class = TicketMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_create(self, serializer):
        ticket = get_object_or_404(
            SupportTicket, 
            id=self.kwargs['ticket_id'],
            customer=self.request.user
        )
        serializer.save(ticket=ticket, sender=self.request.user)


class FAQListView(generics.ListAPIView):
    """List published FAQs."""
    
    serializer_class = FAQSerializer
    permission_classes = []
    
    def get_queryset(self):
        return FAQ.objects.filter(is_published=True).order_by('order', 'question')


class ProductReviewListView(generics.ListCreateAPIView):
    """List and create product reviews."""
    
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductReview.objects.filter(
            product_id=self.kwargs['product_id'],
            is_approved=True
        ).order_by('-created_at')


class ProductReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete product review."""
    
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductReview.objects.filter(customer=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_review(request, review_id):
    """Vote on a review."""
    review = get_object_or_404(ProductReview, id=review_id)
    is_helpful = request.data.get('is_helpful', True)
    
    vote, created = ReviewVote.objects.get_or_create(
        review=review,
        user=request.user,
        defaults={'is_helpful': is_helpful}
    )
    
    if not created:
        vote.is_helpful = is_helpful
        vote.save()
    
    # Update helpful votes count
    review.helpful_votes = review.votes.filter(is_helpful=True).count()
    review.save(update_fields=['helpful_votes'])
    
    return Response({'status': 'success'})