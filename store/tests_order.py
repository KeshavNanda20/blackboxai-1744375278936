from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth.models import User
from .models import Product, Category, Cart, CartItem, Order

class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.admin = User.objects.create_superuser(username='admin', password='adminpass')
        self.category = Category.objects.create(name='TestCategory', icon='icon')
        self.product = Product.objects.create(
            name='TestProduct',
            price=10.00,
            quantity='1 kg',
            image='http://example.com/image.jpg',
            category=self.category,
            description='Test product'
        )
        self.client = APIClient()
        self.client.login(username='testuser', password='testpass')
        self.cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(cart=self.cart, product=self.product, quantity=2)

    def test_checkout_without_address(self):
        url = reverse('order-checkout')
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('delivery_address', response.data.get('error', '') or '')

    def test_checkout_with_address(self):
        url = reverse('order-checkout')
        data = {'delivery_address': '123 Test Street'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['delivery_address'], '123 Test Street')
        self.assertEqual(response.data['status'], 'pending')

    def test_order_acceptance_by_admin(self):
        # Create order
        order = Order.objects.create(user=self.user, total=20.00, delivery_address='123 Test Street')
        url = reverse('order-accept-order', args=[order.id])
        # Non-admin user should be forbidden
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        # Admin user can accept order
        self.client.logout()
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.status, 'processing')

    def test_order_tracking(self):
        order = Order.objects.create(user=self.user, total=20.00, delivery_address='123 Test Street')
        url = reverse('order-tracking', args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['order_id'], order.id)

    def test_order_rating(self):
        order = Order.objects.create(user=self.user, total=20.00, delivery_address='123 Test Street', status='delivered')
        url = reverse('order-rate', args=[order.id])
        # Invalid rating
        response = self.client.post(url, {'rating': 6})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Valid rating
        response = self.client.post(url, {'rating': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        order.refresh_from_db()
        self.assertEqual(order.rating, 4)
