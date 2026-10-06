from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.common.models import TimeStampedModel
from apps.products.models import Product

class BatchStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active / In Stock'
    DEPLETED = 'DEPLETED', 'Depleted / Sold Out'
    EXPIRED = 'EXPIRED', 'Expired / Quarantine'
    RECALLED = 'RECALLED', 'Recalled'


class Batch(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    batch_number = models.CharField(max_length=100, db_index=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(db_index=True)
    initial_quantity = models.PositiveIntegerField(default=0)
    current_quantity = models.PositiveIntegerField(default=0)
    supplier = models.CharField(max_length=150, blank=True)
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=30, choices=BatchStatus.choices, default=BatchStatus.ACTIVE)

    class Meta:
        ordering = ['expiry_date']
        verbose_name_plural = 'Batches'
        unique_together = ('product', 'batch_number')

    def __str__(self):
        return f"{self.product.name} - Batch {self.batch_number} (Exp: {self.expiry_date})"

    @property
    def is_expired(self):
        return self.expiry_date <= timezone.now().date()

    @property
    def is_expiring_soon(self):
        if not self.is_expired:
            delta = (self.expiry_date - timezone.now().date()).days
            return delta <= 60
        return False


class TransactionType(models.TextChoices):
    PURCHASE = 'PURCHASE', 'Purchase / Stock In'
    SALE = 'SALE', 'Customer Order / Stock Out'
    RETURN = 'RETURN', 'Customer Return'
    ADJUSTMENT = 'ADJUSTMENT', 'Manual Adjustment'
    EXPIRED = 'EXPIRED', 'Expired Disposal'
    DAMAGED = 'DAMAGED', 'Damaged Loss'
    CORRECTION = 'CORRECTION', 'Inventory Audit Correction'


class StockTransaction(models.Model):
    """
    Immutable audit history of every stock modification.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_transactions')
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=30, choices=TransactionType.choices, db_index=True)
    quantity = models.IntegerField(help_text="Positive for addition, negative for deduction")
    previous_stock = models.PositiveIntegerField()
    new_stock = models.PositiveIntegerField()
    reference = models.CharField(max_length=100, blank=True, help_text="e.g. PO-881, Order #ORD-2026-101")
    notes = models.TextField(blank=True)
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_adjustments'
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.transaction_type} {self.quantity} on {self.product.name} at {self.created_at.strftime('%Y-%m-%d %H:%M')}"
