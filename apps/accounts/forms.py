from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, Profile, Address

class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email


class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'phone')


class ProfileDetailsForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('avatar', 'date_of_birth', 'blood_group', 'bio')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 3}),
        }


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('title', 'full_name', 'phone', 'address_line', 'area', 'city', 'province', 'postal_code', 'landmark', 'is_default')
        widgets = {
            'address_line': forms.TextInput(attrs={'placeholder': 'House #, Street name'}),
            'landmark': forms.TextInput(attrs={'placeholder': 'Near hospital, school, etc.'}),
        }
