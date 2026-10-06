from django import forms
from .models import Batch, StockTransaction, TransactionType
from apps.products.models import Product

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['product', 'batch_number', 'manufacturing_date', 'expiry_date', 'initial_quantity', 'current_quantity', 'supplier', 'cost_per_unit', 'status']
        widgets = {
            'manufacturing_date': forms.DateInput(attrs={'type': 'date'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
        }


class StockAdjustmentForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.filter(active=True))
    batch = forms.ModelChoiceField(queryset=Batch.objects.all(), required=False)
    transaction_type = forms.ChoiceField(choices=TransactionType.choices)
    quantity = forms.IntegerField(help_text="Positive to add stock, negative to remove")
    reference = forms.CharField(max_length=100, required=False, help_text="e.g. PO-899, Cycle-Count-Q1")
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
