from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from apps.products.models import Category, Product

class ProductModelTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Antibiotics', slug='antibiotics')
        self.product = Product.objects.create(
            name='Amoxicillin 500mg',
            slug='amoxicillin-500mg',
            sku='MED-AMOX-500',
            generic_name='Amoxicillin',
            brand='GSK',
            category=self.category,
            dosage_form='Capsule',
            strength='500mg',
            description='Broad-spectrum antibiotic.',
            price=Decimal('15.00'),
            discount_price=Decimal('12.00'),
            stock_quantity=50,
            min_stock_level=10,
            prescription_required=True
        )

    def test_product_effective_price(self):
        self.assertEqual(self.product.effective_price, Decimal('12.00'))

    def test_product_discount_percentage(self):
        self.assertEqual(self.product.discount_percent, 20)

    def test_product_in_stock(self):
        self.assertTrue(self.product.in_stock)

    def test_product_catalog_view(self):
        response = self.client.get(reverse('products:product_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amoxicillin')

    def test_product_search_view(self):
        response = self.client.get(reverse('products:search') + '?q=Amoxicillin')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Amoxicillin')
