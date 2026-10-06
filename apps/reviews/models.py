from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.common.models import TimeStampedModel
from apps.products.models import Product
from apps.orders.models import Order

class Review(TimeStampedModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviews')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating between 1 and 5 stars"
    )
    review = models.TextField()
    approved = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('customer', 'product')

    def __str__(self):
        return f"{self.rating}* by {self.customer.username} on {self.product.name}"
