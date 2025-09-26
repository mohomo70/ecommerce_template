from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from decimal import Decimal
from .models import Category, Product, ProductVariant, ProductImage


class CategoryModelTest(TestCase):
    def setUp(self):
        self.parent_category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            description='Electronic devices'
        )
        self.child_category = Category.objects.create(
            name='Smartphones',
            slug='smartphones',
            description='Mobile phones',
            parent=self.parent_category
        )
    
    def test_category_creation(self):
        self.assertEqual(self.parent_category.name, 'Electronics')
        self.assertEqual(self.child_category.parent, self.parent_category)
    
    def test_category_full_path(self):
        self.assertEqual(self.child_category.full_path, 'Electronics > Smartphones')


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics'
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
    
    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Test Product')
        self.assertEqual(self.product.category, self.category)
    
    def test_price_range_single_variant(self):
        self.assertEqual(self.product.price_range, '$99.99')
    
    def test_price_range_multiple_variants(self):
        ProductVariant.objects.create(
            product=self.product,
            sku='TEST-002',
            price=Decimal('149.99'),
            stock_quantity=5
        )
        self.assertEqual(self.product.price_range, '$99.99 - $149.99')


class ProductAPITest(APITestCase):
    def setUp(self):
        self.category = Category.objects.create(
            name='Electronics',
            slug='electronics',
            is_active=True
        )
        self.product = Product.objects.create(
            name='Test Product',
            slug='test-product',
            description='A test product',
            category=self.category,
            is_active=True
        )
        self.variant = ProductVariant.objects.create(
            product=self.product,
            sku='TEST-001',
            price=Decimal('99.99'),
            stock_quantity=10,
            is_active=True
        )
    
    def test_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_detail(self):
        url = reverse('product-detail', kwargs={'slug': 'test-product'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Product')
    
    def test_product_search(self):
        url = reverse('product-search')
        response = self.client.get(url, {'q': 'test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_category_list(self):
        url = reverse('category-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_product_filtering(self):
        url = reverse('product-list')
        response = self.client.get(url, {'category_slug': 'electronics'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_product_price_filtering(self):
        url = reverse('product-list')
        response = self.client.get(url, {'min_price': '50', 'max_price': '150'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)