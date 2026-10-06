from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    RATING_CHOICES = [
        (5, '5 Stars - Excellent'),
        (4, '4 Stars - Very Good'),
        (3, '3 Stars - Good / Average'),
        (2, '2 Stars - Fair'),
        (1, '1 Star - Poor'),
    ]
    rating = forms.ChoiceField(choices=RATING_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = Review
        fields = ['rating', 'review']
        widgets = {
            'review': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Write your honest feedback regarding product quality, packaging, and effectiveness...'}),
        }
