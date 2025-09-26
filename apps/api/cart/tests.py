from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from accounts.models import User
from catalog.models import Category, Product, ProductVariant
from .models import Cart, CartItem


class CartModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='A test product',
            category=self.category
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.cart = Cart.objects.create(user=self.user)
    
    def test_cart_creation(self):
        self.assertEqual(self.cart.user, self.user)
        self.assertEqual(self.cart.total_items, 0)
        self.assertEqual(self.cart.subtotal, Decimal('0.00'))
    
    def test_cart_item_creation(self):
        cart_item = CartItem.objects.create(
            cart=self.cart,
            variant=self.variant,
            quantity=2
        )
        self.assertEqual(cart_item.cart, self.cart)
        self.assertEqual(cart_item.variant, self.variant)
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.line_total, Decimal('199.98'))
    
    def test_cart_totals(self):
        CartItem.objects.create(
            cart=self.cart,
            variant=self.variant,
            quantity=2
        )
        self.assertEqual(self.cart.total_items, 2)
        self.assertEqual(self.cart.subtotal, Decimal('199.98'))
        self.assertEqual(self.cart.tax_amount, Decimal('19.998'))
        self.assertEqual(self.cart.total, Decimal('219.978'))


class CartAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Test Category',
            slug='test-category'
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='A test product',
            category=self.category
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('99.99'),
            stock_quantity=10
        )
        self.client.force_authenticate(user=self.user)
    
    def test_get_cart(self):
        url = reverse('cart-detail')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_add_to_cart(self):
        url = reverse('cart-item-create')
        data = {
            'variant_id': self.variant.id,
            'quantity': 2
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Check cart was updated
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_items, 2)
    
    def test_update_cart_item(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1
        )
        
        url = reverse('cart-item-update', kwargs={'item_id': cart_item.id})
        data = {'quantity': 3}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 3)
    
    def test_remove_from_cart(self):
        cart = Cart.objects.create(user=self.user)
        cart_item = CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1
        )
        
        url = reverse('cart-item-delete', kwargs={'item_id': cart_item.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_clear_cart(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=1
        )
        
        url = reverse('cart-clear')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertEqual(cart.items.count(), 0)
    
    def test_cart_totals(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            variant=self.variant,
            quantity=2
        )
        
        url = reverse('cart-totals')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        totals = response.data
        self.assertEqual(totals['item_count'], 2)
        self.assertEqual(float(totals['subtotal']), 199.98)
    
    def test_stock_validation(self):
        url = reverse('cart-item-create')
        data = {
            'variant_id': self.variant.id,
            'quantity': 15  # More than available stock
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)