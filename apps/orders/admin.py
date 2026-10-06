from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name_snapshot', 'sku_snapshot', 'quantity', 'unit_price', 'tax', 'subtotal', 'prescription_required')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer', 'grand_total', 'payment_method', 'payment_status', 'order_status', 'requires_prescription', 'created_at')
    list_filter = ('order_status', 'payment_status', 'payment_method', 'requires_prescription', 'created_at')
    search_fields = ('order_number', 'customer__username', 'customer__email', 'shipping_address_snapshot')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'shipping_address_snapshot', 'subtotal', 'tax', 'delivery_fee', 'grand_total')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
