from django import forms
from apps.accounts.models import Address
from apps.prescriptions.models import Prescription
from .models import PaymentMethod, OrderStatus

class CheckoutForm(forms.Form):
    shipping_address = forms.ModelChoiceField(
        queryset=Address.objects.none(),
        widget=forms.RadioSelect,
        empty_label=None
    )
    payment_method = forms.ChoiceField(
        choices=PaymentMethod.choices,
        widget=forms.RadioSelect,
        initial=PaymentMethod.COD
    )
    prescription = forms.ModelChoiceField(
        queryset=Prescription.objects.none(),
        required=False,
        empty_label="-- Select an uploaded prescription --"
    )
    customer_notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional delivery notes, buzzer code, or drop-off preferences'}),
        required=False
    )

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['shipping_address'].queryset = Address.objects.filter(user=user)
        self.fields['prescription'].queryset = Prescription.objects.filter(customer=user)


class OrderStatusUpdateForm(forms.Form):
    order_status = forms.ChoiceField(choices=OrderStatus.choices)
    staff_notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False)
