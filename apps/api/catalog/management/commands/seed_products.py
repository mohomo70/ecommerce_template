from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
import random
from catalog.models import Category, Product, ProductVariant, ProductImage


class Command(BaseCommand):
    help = 'Seed the database with sample products and categories'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=100,
            help='Number of products to create (default: 100)'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        with transaction.atomic():
            self.create_categories()
            self.create_products(count)
            
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {count} products with categories and variants')
        )
    
    def create_categories(self):
        """Create sample categories."""
        categories_data = [
            {
                'name': 'Electronics',
                'slug': 'electronics',
                'description': 'Electronic devices and gadgets',
                'children': [
                    {'name': 'Smartphones', 'slug': 'smartphones', 'description': 'Mobile phones and accessories'},
                    {'name': 'Laptops', 'slug': 'laptops', 'description': 'Laptop computers and accessories'},
                    {'name': 'Audio', 'slug': 'audio', 'description': 'Headphones, speakers, and audio equipment'},
                ]
            },
            {
                'name': 'Clothing',
                'slug': 'clothing',
                'description': 'Fashion and apparel',
                'children': [
                    {'name': 'Men\'s Clothing', 'slug': 'mens-clothing', 'description': 'Clothing for men'},
                    {'name': 'Women\'s Clothing', 'slug': 'womens-clothing', 'description': 'Clothing for women'},
                    {'name': 'Accessories', 'slug': 'accessories', 'description': 'Fashion accessories'},
                ]
            },
            {
                'name': 'Home & Garden',
                'slug': 'home-garden',
                'description': 'Home improvement and garden supplies',
                'children': [
                    {'name': 'Furniture', 'slug': 'furniture', 'description': 'Home and office furniture'},
                    {'name': 'Kitchen', 'slug': 'kitchen', 'description': 'Kitchen appliances and tools'},
                    {'name': 'Garden', 'slug': 'garden', 'description': 'Garden tools and supplies'},
                ]
            },
            {
                'name': 'Sports',
                'slug': 'sports',
                'description': 'Sports and fitness equipment',
                'children': [
                    {'name': 'Fitness', 'slug': 'fitness', 'description': 'Fitness equipment and accessories'},
                    {'name': 'Outdoor', 'slug': 'outdoor', 'description': 'Outdoor sports equipment'},
                    {'name': 'Team Sports', 'slug': 'team-sports', 'description': 'Team sports equipment'},
                ]
            }
        ]
        
        for cat_data in categories_data:
            parent_cat, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'description': cat_data['description']
                }
            )
            
            for child_data in cat_data['children']:
                Category.objects.get_or_create(
                    slug=child_data['slug'],
                    defaults={
                        'name': child_data['name'],
                        'description': child_data['description'],
                        'parent': parent_cat
                    }
                )
    
    def create_products(self, count):
        """Create sample products."""
        categories = list(Category.objects.filter(parent__isnull=False))
        
        product_names = [
            'Premium Wireless Headphones', 'Smart Fitness Tracker', 'Ergonomic Office Chair',
            'Professional Camera Lens', 'Organic Cotton T-Shirt', 'Stainless Steel Water Bottle',
            'LED Desk Lamp', 'Bluetooth Speaker', 'Yoga Mat', 'Wireless Mouse',
            'Mechanical Keyboard', 'Portable Power Bank', 'Running Shoes', 'Backpack',
            'Coffee Maker', 'Smart Watch', 'Gaming Mouse Pad', 'Phone Case',
            'Laptop Stand', 'Desk Organizer', 'Plant Pot', 'Wall Clock',
            'Throw Pillow', 'Table Lamp', 'Picture Frame', 'Candles Set',
            'Bath Towel', 'Shower Curtain', 'Kitchen Knife Set', 'Cutting Board',
            'Dining Table', 'Office Desk', 'Bookshelf', 'Sofa',
            'Coffee Table', 'Dining Chairs', 'Bed Frame', 'Mattress',
            'Pillow', 'Blanket', 'Curtains', 'Rug',
            'Mirror', 'Vase', 'Artwork', 'Sculpture'
        ]
        
        colors = ['Black', 'White', 'Red', 'Blue', 'Green', 'Yellow', 'Purple', 'Orange', 'Pink', 'Gray']
        sizes = ['XS', 'S', 'M', 'L', 'XL', 'XXL']
        materials = ['Cotton', 'Polyester', 'Leather', 'Metal', 'Plastic', 'Wood', 'Glass', 'Ceramic']
        
        for i in range(count):
            category = random.choice(categories)
            base_name = random.choice(product_names)
            color = random.choice(colors)
            material = random.choice(materials)
            
            product_name = f"{color} {material} {base_name}"
            slug = f"{product_name.lower().replace(' ', '-')}-{i+1}"
            
            product = Product.objects.create(
                name=product_name,
                slug=slug,
                description=f"High-quality {product_name.lower()} perfect for everyday use. Made from premium {material.lower()} materials and available in {color.lower()}.",
                short_description=f"Premium {material.lower()} {base_name.lower()} in {color.lower()}",
                category=category,
                attributes={
                    'color': color,
                    'material': material,
                    'brand': f'Brand {random.randint(1, 10)}',
                    'warranty': f'{random.randint(1, 5)} years'
                },
                is_featured=random.choice([True, False])
            )
            
            # Create 1-5 variants for each product
            variant_count = random.randint(1, 5)
            for j in range(variant_count):
                size = random.choice(sizes) if random.choice([True, False]) else None
                variant_name = f"{size} {color}" if size else color
                sku = f"{product.slug}-{j+1}"
                
                base_price = Decimal(str(random.uniform(10, 500)))
                compare_price = base_price * Decimal('1.2') if random.choice([True, False]) else None
                
                variant = ProductVariant.objects.create(
                    product=product,
                    sku=sku,
                    name=variant_name,
                    price=base_price,
                    compare_at_price=compare_price,
                    cost_price=base_price * Decimal('0.6'),
                    stock_quantity=random.randint(0, 100),
                    track_inventory=random.choice([True, False]),
                    weight=Decimal(str(random.uniform(0.1, 5.0))),
                    dimensions={
                        'length': random.randint(10, 100),
                        'width': random.randint(10, 100),
                        'height': random.randint(10, 100)
                    }
                )
            
            # Create 1-3 images for each product (placeholder)
            for k in range(random.randint(1, 3)):
                ProductImage.objects.create(
                    product=product,
                    image=f'products/placeholder-{random.randint(1, 10)}.jpg',
                    alt_text=f"{product.name} - Image {k+1}",
                    is_primary=(k == 0),
                    sort_order=k
                )
