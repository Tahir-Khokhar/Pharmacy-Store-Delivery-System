from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.common.utils import generate_unique_code
from apps.accounts.models import Address
from apps.products.models import Product
from apps.prescriptions.models import Prescription

class OrderStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Confirmation'
    PRESCRIPTION_REVIEW = 'PRESCRIPTION_REVIEW', 'Awaiting Prescription Review'
    CONFIRMED = 'CONFIRMED', 'Confirmed'
    PROCESSING = 'PROCESSING', 'Processing & Packaging'
    PACKED = 'PACKED', 'Packed & Ready'
    READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Ready for Dispatch'
    OUT_FOR_DELIVERY = 'OUT_FOR_DELIVERY', 'Out for Delivery'
    DELIVERED = 'DELIVERED', 'Delivered'
    CANCELLED = 'CANCELLED', 'Cancelled'
    REFUNDED = 'REFUNDED', 'Refunded'


class PaymentMethod(models.TextChoices):
    COD = 'COD', 'Cash on Delivery'
    ONLINE = 'ONLINE', 'Card / Digital Payment'


class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Payment Pending'
    PROCESSING = 'PROCESSING', 'Processing'
    PAID = 'PAID', 'Paid'
    FAILED = 'FAILED', 'Payment Failed'
    REFUNDED = 'REFUNDED', 'Refunded'


class Order(TimeStampedModel):
    order_number = models.CharField(max_length=50, unique=True, db_index=True)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    shipping_address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address_snapshot = models.TextField(help_text="Immutable snapshot of shipping address at checkout")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=30, choices=PaymentMethod.choices, default=PaymentMethod.COD)
    payment_status = models.CharField(max_length=30, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    order_status = models.CharField(max_length=30, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True)
    requires_prescription = models.BooleanField(default=False, db_index=True)
    prescription = models.ForeignKey(
        Prescription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        help_text="Attached prescription required for verification"
    )
    customer_notes = models.TextField(blank=True)
    staff_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_number} - {self.customer.username} (${self.grand_total})"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = generate_unique_code(prefix='ORD')
        super().save(*args, **kwargs)

    @property
    def can_be_cancelled(self):
        return self.order_status in [OrderStatus.PENDING, OrderStatus.PRESCRIPTION_REVIEW, OrderStatus.CONFIRMED]

    @property
    def is_delivered(self):
        return self.order_status == OrderStatus.DELIVERED

    @property
    def prescription_satisfied(self):
        if not self.requires_prescription:
            return True
        return bool(self.prescription and self.prescription.is_approved)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items')
    product_name_snapshot = models.CharField(max_length=200)
    sku_snapshot = models.CharField(max_length=60)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    prescription_required = models.BooleanField(default=False)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.quantity}x {self.product_name_snapshot} in #{self.order.order_number}"
