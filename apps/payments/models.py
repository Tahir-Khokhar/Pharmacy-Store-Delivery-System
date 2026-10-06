from django.db import models
from django.utils import timezone
from apps.common.models import TimeStampedModel
from apps.common.utils import generate_unique_code

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Payment'
    PROCESSING = 'PROCESSING', 'Processing'
    PAID = 'PAID', 'Paid Successfully'
    FAILED = 'FAILED', 'Failed'
    REFUNDED = 'REFUNDED', 'Refunded'
    CANCELLED = 'CANCELLED', 'Cancelled'


class Payment(TimeStampedModel):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True, db_index=True)
    payment_method = models.CharField(max_length=30)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    gateway_response = models.TextField(blank=True, help_text="Mock/Gateway payload response details")
    paid_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment #{self.transaction_id} for Order #{self.order.order_number} (${self.amount})"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = generate_unique_code(prefix='TXN')
        super().save(*args, **kwargs)

    def mark_as_paid(self, gateway_note=""):
        self.status = PaymentStatus.PAID
        self.paid_at = timezone.now()
        if gateway_note:
            self.gateway_response = gateway_note
        self.save()
        self.order.payment_status = 'PAID'
        self.order.save(update_fields=['payment_status'])
