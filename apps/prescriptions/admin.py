from django.contrib import admin
from .models import Prescription

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('prescription_number', 'customer', 'status', 'doctor_name', 'verified_by', 'verified_at', 'created_at')
    list_filter = ('status', 'created_at', 'verified_at')
    search_fields = ('prescription_number', 'customer__username', 'customer__email', 'doctor_name', 'clinic_hospital')
    readonly_fields = ('prescription_number', 'created_at', 'updated_at')
    date_hierarchy = 'created_at'
