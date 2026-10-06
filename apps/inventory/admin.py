from django.contrib import admin
from .models import Batch, StockTransaction

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('product', 'batch_number', 'current_quantity', 'initial_quantity', 'expiry_date', 'status', 'supplier')
    list_filter = ('status', 'expiry_date')
    search_fields = ('product__name', 'batch_number', 'supplier')
    date_hierarchy = 'expiry_date'

@admin.register(StockTransaction)
class StockTransactionAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'product', 'transaction_type', 'quantity', 'previous_stock', 'new_stock', 'performed_by', 'reference')
    list_filter = ('transaction_type', 'created_at')
    search_fields = ('product__name', 'reference', 'notes', 'performed_by__username')
    readonly_fields = ('created_at', 'product', 'batch', 'transaction_type', 'quantity', 'previous_stock', 'new_stock', 'reference', 'notes', 'performed_by')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
