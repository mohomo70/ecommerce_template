from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order


@receiver(post_save, sender=Order)
def award_points_on_payment(sender, instance, created, **kwargs):
    """Award points when order status changes to paid."""
    if not created and instance.status == 'paid':
        # Award 1 point per dollar spent (rounded down)
        points_to_award = int(instance.total)
        if points_to_award > 0:
            instance.user.add_points(
                points_to_award, 
                f"Order {instance.order_number} payment"
            )
