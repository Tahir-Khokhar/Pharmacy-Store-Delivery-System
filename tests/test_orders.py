from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.models import Address
from apps.products.models import Category, Product
from apps.cart.models import Cart, CartItem
from apps.orders.services import OrderService, OrderProcessingError
from apps.orders.models import OrderStatus

User = get_user_model()

class OrderProcessingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='orderuser', email='ord@test.com', password='password123')
        self.address = Address.objects.create(
            user=self.user,
            full_name='Test User',
            phone='+15550001',
            address_line='123 Health St',
            city='Careville',
            postal_code='12345'
        )
        self.category = Category.objects.create(name='Vitamins', slug='vitamins')
        self.product = Product.objects.create(
            name='Vitamin C 1000mg',
            slug='vitamin-c-1000mg',
            sku='VIT-C-1000',
            brand='NatureCare',
            category=self.category,
            price=Decimal('15.00'),
            tax_rate=Decimal('5.00'),
            stock_quantity=20,
            prescription_required=False
        )
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_order_creation_and_stock_deduction(self):
        initial_stock = self.product.stock_quantity
        order = OrderService.process_checkout(
            user=self.user,
            cart=self.cart,
            shipping_address=self.address,
            payment_method='COD'
        )

        self.assertIsNotNone(order.order_number)
        self.assertEqual(order.order_status, OrderStatus.CONFIRMED)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_quantity, initial_stock - 2)
        self.assertEqual(self.cart.items.count(), 0)
        self.assertTrue(hasattr(order, 'delivery'))
        self.assertTrue(hasattr(order, 'payment'))

    def test_prescription_required_enforcement(self):
        rx_product = Product.objects.create(
            name='Controlled Rx Medicine',
            slug='controlled-rx',
            sku='RX-100',
            brand='PharmaTech',
            category=self.category,
            price=Decimal('50.00'),
            stock_quantity=10,
            prescription_required=True
        )
        CartItem.objects.create(cart=self.cart, product=rx_product, quantity=1)

        with self.assertRaises(OrderProcessingError):
            OrderService.process_checkout(
                user=self.user,
                cart=self.cart,
                shipping_address=self.address,
                payment_method='COD',
                prescription=None
            )
