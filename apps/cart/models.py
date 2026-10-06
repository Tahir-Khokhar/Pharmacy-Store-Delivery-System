from decimal import Decimal
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.products.models import Product

class Cart(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        user_str = self.user.username if self.user else f"Guest ({self.session_key})"
        return f"Cart: {user_str}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.item_subtotal for item in self.items.all())

    @property
    def tax_total(self):
        total_tax = Decimal('0.00')
        for item in self.items.all():
            rate = Decimal(str(item.product.tax_rate or 5.0)) / Decimal('100.0')
            total_tax += item.item_subtotal * rate
        return round(total_tax, 2)

    @property
    def delivery_fee(self):
        # Free delivery over $50, else $4.99 standard
        if self.subtotal == 0 or self.subtotal >= Decimal('50.00'):
            return Decimal('0.00')
        return Decimal('4.99')

    @property
    def grand_total(self):
        return self.subtotal + self.tax_total + self.delivery_fee

    @property
    def has_prescription_items(self):
        return self.items.filter(product__prescription_required=True).exists()


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product')
        ordering = ['created_at']

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

    @property
    def item_subtotal(self):
        return self.product.effective_price * self.quantity
