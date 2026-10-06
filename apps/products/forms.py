from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'sku', 'generic_name', 'brand', 'category', 'dosage_form',
            'strength', 'description', 'short_description', 'image', 'price',
            'discount_price', 'tax_rate', 'stock_quantity', 'min_stock_level',
            'unit', 'manufacturer', 'batch_number', 'manufacturing_date',
            'expiry_date', 'prescription_required', 'active', 'featured'
        ]
        widgets = {
            'manufacturing_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'short_description': forms.Textarea(attrs={'rows': 2}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'image', 'icon', 'parent', 'active']
