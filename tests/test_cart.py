from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.products.models import Category, Product
from apps.cart.models import Cart, CartItem

User = get_user_model()

class CartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testcustomer', email='cust@test.com', password='password123')
        self.category = Category.objects.create(name='Pain Relief', slug='pain-relief')
        self.product = Product.objects.create(
            name='Ibuprofen 400mg',
            slug='ibuprofen-400mg',
            sku='MED-IBU-400',
            brand='Advil',
            category=self.category,
            price=Decimal('10.00'),
            tax_rate=Decimal('5.00'),
            stock_quantity=20
        )

    def test_add_to_cart_ajax(self):
        self.client.login(username='testcustomer', password='password123')
        response = self.client.post(reverse('cart:add_ajax'), {
            'product_id': self.product.id,
            'quantity': 2
        })
        self.assertEqual(response.status_code, 200)
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_items, 2)
        self.assertEqual(cart.subtotal, Decimal('20.00'))

    def test_cart_tax_and_delivery_fee(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)
        self.assertEqual(cart.subtotal, Decimal('20.00'))
        self.assertEqual(cart.tax_total, Decimal('1.00'))
        self.assertEqual(cart.delivery_fee, Decimal('4.99'))  # Under $50
        self.assertEqual(cart.grand_total, Decimal('25.99'))

    def test_cart_free_delivery_over_threshold(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=cart, product=self.product, quantity=6) # 6 * 10 = $60
        self.assertEqual(cart.delivery_fee, Decimal('0.00'))
