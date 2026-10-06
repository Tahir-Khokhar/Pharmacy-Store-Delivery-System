from django.contrib import admin
from .models import Category, Product, ProductImage, Wishlist

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'icon', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'generic_name', 'brand', 'category', 'price', 'discount_price',
        'stock_quantity', 'min_stock_level', 'prescription_required', 'active', 'expiry_date'
    )
    list_filter = ('category', 'prescription_required', 'active', 'featured', 'dosage_form')
    search_fields = ('name', 'generic_name', 'brand', 'sku', 'manufacturer')
    prepopulated_fields = {'slug': ('name', 'brand')}
    inlines = [ProductImageInline]
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'sku', 'generic_name', 'brand', 'category', 'dosage_form', 'strength')
        }),
        ('Descriptions & Media', {
            'fields': ('short_description', 'description', 'image')
        }),
        ('Pricing & Inventory', {
            'fields': ('price', 'discount_price', 'tax_rate', 'stock_quantity', 'min_stock_level', 'unit')
        }),
        ('Clinical & Batch Details', {
            'fields': ('manufacturer', 'batch_number', 'manufacturing_date', 'expiry_date', 'prescription_required')
        }),
        ('Status & Visibility', {
            'fields': ('active', 'featured')
        }),
    )

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__username', 'product__name')
