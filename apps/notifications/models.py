from django.db import models
from django.conf import settings

class NotificationType(models.TextChoices):
    ORDER_PLACED = 'ORDER_PLACED', 'Order Placed'
    ORDER_CONFIRMED = 'ORDER_CONFIRMED', 'Order Confirmed'
    ORDER_PROCESSING = 'ORDER_PROCESSING', 'Order In Processing'
    ORDER_SHIPPED = 'ORDER_SHIPPED', 'Order Out For Delivery'
    ORDER_DELIVERED = 'ORDER_DELIVERED', 'Order Delivered'
    PRESCRIPTION_APPROVED = 'PRESCRIPTION_APPROVED', 'Prescription Approved'
    PRESCRIPTION_REJECTED = 'PRESCRIPTION_REJECTED', 'Prescription Rejected'
    LOW_STOCK = 'LOW_STOCK', 'Low Stock Alert'
    PAYMENT_SUCCESS = 'PAYMENT_SUCCESS', 'Payment Successful'
    PAYMENT_FAILED = 'PAYMENT_FAILED', 'Payment Failed'


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=40, choices=NotificationType.choices, default=NotificationType.ORDER_PLACED)
    is_read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.title} ({'Read' if self.is_read else 'Unread'})"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=['is_read'])
