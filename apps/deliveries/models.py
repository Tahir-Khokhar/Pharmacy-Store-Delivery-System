from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.common.utils import generate_unique_code

class DeliveryStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Assignment'
    ASSIGNED = 'ASSIGNED', 'Assigned to Driver'
    PICKED_UP = 'PICKED_UP', 'Picked Up from Pharmacy'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
    DELIVERED = 'DELIVERED', 'Delivered to Customer'
    FAILED = 'FAILED', 'Delivery Attempt Failed'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Delivery(TimeStampedModel):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='delivery')
    delivery_staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_deliveries'
    )
    tracking_number = models.CharField(max_length=60, unique=True, db_index=True)
    delivery_address = models.TextField()
    status = models.CharField(
        max_length=30,
        choices=DeliveryStatus.choices,
        default=DeliveryStatus.PENDING,
        db_index=True
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    out_for_delivery_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    delivery_notes = models.TextField(blank=True, help_text="Gate codes, delivery confirmations, recipient handover notes")
    recipient_name = models.CharField(max_length=150, blank=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Deliveries'

    def __str__(self):
        return f"Tracking #{self.tracking_number} (Order #{self.order.order_number}) - {self.status}"

    def save(self, *args, **kwargs):
        if not self.tracking_number:
            self.tracking_number = generate_unique_code(prefix='TRK')
        super().save(*args, **kwargs)
