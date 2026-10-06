import datetime
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.conf import settings
from apps.common.models import TimeStampedModel

class DosageForm(models.TextChoices):
    TABLET = 'Tablet', 'Tablet'
    CAPSULE = 'Capsule', 'Capsule'
    SYRUP = 'Syrup', 'Syrup'
    INJECTION = 'Injection', 'Injection'
    CREAM = 'Cream', 'Cream / Ointment'
    DROPS = 'Drops', 'Eye/Ear Drops'
    INHALER = 'Inhaler', 'Inhaler'
    SPRAY = 'Spray', 'Nasal / Oral Spray'
    GEL = 'Gel', 'Gel'
    POWDER = 'Powder', 'Powder'
    SUPPLEMENT = 'Supplement', 'Dietary Supplement'
    DEVICE = 'Device', 'Medical Device'
    CARE = 'Care', 'Personal Care'
    OTHER = 'Other', 'Other Healthcare'


class Category(TimeStampedModel):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, default='bi-capsule', help_text='Bootstrap icon class')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=220, unique=True)
    sku = models.CharField(max_length=60, unique=True, help_text="Stock Keeping Unit / Barcode")
    generic_name = models.CharField(max_length=200, db_index=True, blank=True, help_text="e.g. Paracetamol, Amoxicillin")
    brand = models.CharField(max_length=150, db_index=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name='products')
    dosage_form = models.CharField(max_length=50, choices=DosageForm.choices, default=DosageForm.TABLET)
    strength = models.CharField(max_length=50, blank=True, help_text="e.g. 500mg, 10mg/5ml")
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=5.00, help_text="Percentage e.g. 5.00%")
    stock_quantity = models.PositiveIntegerField(default=0)
    min_stock_level = models.PositiveIntegerField(default=10, help_text="Alert threshold for low stock")
    unit = models.CharField(max_length=50, default='Box of 20', help_text="e.g. Strip of 10, 100ml Bottle")
    manufacturer = models.CharField(max_length=150)
    batch_number = models.CharField(max_length=100, blank=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True, db_index=True)
    prescription_required = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Requires valid prescription verified by pharmacist before fulfillment"
    )
    active = models.BooleanField(default=True, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name', 'generic_name']),
            models.Index(fields=['brand', 'category']),
        ]

    def __str__(self):
        strength_str = f" ({self.strength})" if self.strength else ""
        return f"{self.name}{strength_str} - {self.brand}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.name}-{self.brand}-{self.sku}")
        super().save(*args, **kwargs)

    @property
    def effective_price(self):
        if self.discount_price and self.discount_price > 0 and self.discount_price < self.price:
            return self.discount_price
        return self.price

    @property
    def discount_percent(self):
        if self.discount_price and self.discount_price < self.price:
            diff = self.price - self.discount_price
            return int((diff / self.price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.stock_quantity > 0

    @property
    def is_low_stock(self):
        return 0 < self.stock_quantity <= self.min_stock_level

    @property
    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date <= timezone.now().date()
        return False

    @property
    def is_expiring_soon(self):
        if self.expiry_date and not self.is_expired:
            today = timezone.now().date()
            delta = (self.expiry_date - today).days
            return delta <= 60
        return False

    @property
    def average_rating(self):
        reviews = self.reviews.filter(approved=True)
        if reviews.exists():
            avg = reviews.aggregate(models.Avg('rating'))['rating__avg']
            return round(avg, 1) if avg else 0
        return 0

    @property
    def reviews_count(self):
        return self.reviews.filter(approved=True).count()


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='additional_images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Gallery Image for {self.product.name}"


class Wishlist(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wishlist_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')

    class Meta:
        unique_together = ('user', 'product')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"
