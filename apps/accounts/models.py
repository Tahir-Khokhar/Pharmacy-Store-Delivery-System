from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.common.models import TimeStampedModel

class UserRole(models.TextChoices):
    CUSTOMER = 'CUSTOMER', 'Customer'
    PHARMACIST = 'PHARMACIST', 'Pharmacist'
    INVENTORY_MANAGER = 'INVENTORY_MANAGER', 'Inventory Manager'
    DELIVERY_STAFF = 'DELIVERY_STAFF', 'Delivery Staff'
    ADMIN = 'ADMIN', 'Administrator'


class User(AbstractUser):
    """
    Custom user model with explicit role assignments for role-based access control.
    """
    role = models.CharField(
        max_length=30,
        choices=UserRole.choices,
        default=UserRole.CUSTOMER,
        db_index=True
    )
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)

    REQUIRED_FIELDS = ['email']

    def is_customer(self):
        return self.role == UserRole.CUSTOMER

    def is_pharmacist(self):
        return self.role == UserRole.PHARMACIST or self.is_superuser

    def is_inventory_manager(self):
        return self.role == UserRole.INVENTORY_MANAGER or self.is_superuser

    def is_delivery_staff(self):
        return self.role == UserRole.DELIVERY_STAFF or self.is_superuser

    def is_admin_user(self):
        return self.role == UserRole.ADMIN or self.is_superuser or self.is_staff

    def get_role_display_name(self):
        return dict(UserRole.choices).get(self.role, self.role)


class Profile(TimeStampedModel):
    """Extended customer/staff profile details."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profiles/', blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=10, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"


class Address(TimeStampedModel):
    """Customer delivery addresses."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=50, default='Home', help_text="e.g. Home, Work, Clinic")
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    address_line = models.CharField(max_length=255)
    area = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    landmark = models.CharField(max_length=150, blank=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_default', '-created_at']
        verbose_name_plural = 'Addresses'

    def __str__(self):
        return f"{self.title}: {self.address_line}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
