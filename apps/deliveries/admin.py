from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('tracking_number', 'order', 'delivery_staff', 'status', 'assigned_at', 'delivered_at')
    list_filter = ('status', 'assigned_at', 'delivered_at')
    search_fields = ('tracking_number', 'order__order_number', 'delivery_staff__username', 'delivery_address')
    readonly_fields = ('tracking_number', 'order', 'delivery_address')
