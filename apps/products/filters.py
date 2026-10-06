import django_filters
from .models import Product, Category, DosageForm

class ProductFilter(django_filters.FilterSet):
    category = django_filters.ModelChoiceFilter(
        queryset=Category.objects.filter(active=True),
        empty_label="All Categories"
    )
    dosage_form = django_filters.ChoiceFilter(
        choices=DosageForm.choices,
        empty_label="All Forms"
    )
    brand = django_filters.CharFilter(lookup_expr='icontains')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    prescription_required = django_filters.BooleanFilter()
    featured = django_filters.BooleanFilter()
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    class Meta:
        model = Product
        fields = ['category', 'dosage_form', 'brand', 'prescription_required', 'featured']

    def filter_in_stock(self, queryset, name, value):
        if value is True:
            return queryset.filter(stock_quantity__gt=0)
        elif value is False:
            return queryset.filter(stock_quantity=0)
        return queryset
