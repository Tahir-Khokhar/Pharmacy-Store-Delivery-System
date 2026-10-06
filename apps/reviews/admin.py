from django.contrib import admin
from .models import Review

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'customer', 'rating', 'approved', 'created_at')
    list_filter = ('rating', 'approved', 'created_at')
    search_fields = ('product__name', 'customer__username', 'review')
