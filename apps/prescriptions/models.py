import os
from django.db import models
from django.conf import settings
from apps.common.models import TimeStampedModel
from apps.common.utils import generate_unique_code

class PrescriptionStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Review'
    UNDER_REVIEW = 'UNDER_REVIEW', 'Under Pharmacist Review'
    APPROVED = 'APPROVED', 'Approved by Pharmacist'
    REJECTED = 'REJECTED', 'Rejected / Invalid'
    EXPIRED = 'EXPIRED', 'Prescription Expired'


def prescription_upload_path(instance, filename):
    return f"prescriptions/user_{instance.customer.id}/{filename}"


class Prescription(TimeStampedModel):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='prescriptions')
    prescription_number = models.CharField(max_length=50, unique=True, db_index=True)
    uploaded_file = models.FileField(upload_to=prescription_upload_path)
    doctor_name = models.CharField(max_length=150, blank=True)
    clinic_hospital = models.CharField(max_length=200, blank=True)
    patient_name = models.CharField(max_length=150, blank=True)
    status = models.CharField(
        max_length=30,
        choices=PrescriptionStatus.choices,
        default=PrescriptionStatus.PENDING,
        db_index=True
    )
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_prescriptions'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.prescription_number} ({self.customer.username}) - {self.status}"

    def save(self, *args, **kwargs):
        if not self.prescription_number:
            self.prescription_number = generate_unique_code(prefix='RX')
        super().save(*args, **kwargs)

    @property
    def is_approved(self):
        return self.status == PrescriptionStatus.APPROVED

    @property
    def file_extension(self):
        name, ext = os.path.splitext(self.uploaded_file.name)
        return ext.lower()

    @property
    def is_image(self):
        return self.file_extension in ['.jpg', '.jpeg', '.png']
