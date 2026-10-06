from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.products.models import Category, Product

User = get_user_model()

class RestApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='apiuser', email='api@test.com', password='password123')
        self.category = Category.objects.create(name='Cardiology', slug='cardiology')
        self.product = Product.objects.create(
            name='Atorvastatin 20mg',
            slug='atorvastatin-20mg',
            sku='MED-ATOR-20',
            brand='Lipitor',
            category=self.category,
            price=Decimal('25.00'),
            stock_quantity=100
        )

    def test_products_list_api(self):
        response = self.client.get('/api/v1/products/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data['results']), 1)

    def test_categories_list_api(self):
        response = self.client.get('/api/v1/categories/')
        self.assertEqual(response.status_code, 200)

    def test_jwt_token_obtain(self):
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'apiuser',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

        # Test authenticated /auth/me/
        token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        me_response = self.client.get('/api/v1/auth/me/')
        self.assertEqual(me_response.status_code, 200)
        self.assertEqual(me_response.data['data']['username'], 'apiuser')

    def test_openapi_schema_endpoint(self):
        response = self.client.get('/api/v1/schema/')
        self.assertEqual(response.status_code, 200)

    def test_swagger_ui_endpoint(self):
        response = self.client.get('/api/v1/docs/')
        self.assertEqual(response.status_code, 200)
