import os
import django
import sys

# Set up Django environment
sys.path.append('d:/TMDT')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Category, Product
from django.utils.text import slugify
from django.contrib.auth.models import User

def seed_data():
    # Create Superuser if not exists
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created superuser: admin/admin123")

    # Create Categories
    # Category.image is optional in seed data because image files are uploaded separately.
    # When no image exists, category_image_url will fall back to a static placeholder.
    categories_data = [
        {'name': 'Smartphone', 'icon': 'fa-mobile-alt'},
        {'name': 'Laptop', 'icon': 'fa-laptop'},
        {'name': 'Máy tính bảng', 'icon': 'fa-tablet-alt'},
        {'name': 'Đồng hồ thông minh', 'icon': 'fa-watch'},
        {'name': 'Tai nghe', 'icon': 'fa-headphones'},
    ]

    for cat in categories_data:
        Category.objects.get_or_create(
            name=cat['name'],
            defaults={'slug': slugify(cat['name']), 'icon': cat['icon']}
        )

    # Create Initial Products
    cats = {c.name: c for c in Category.objects.all()}

    products_data = [
        {
            'category': cats['Smartphone'],
            'name': 'iPhone 15 Pro Max',
            'brand': 'Apple',
            'price': 34990000,
            'old_price': 36990000,
            'description': 'iPhone 15 Pro Max với khung viền Titan siêu bền, chip A17 Pro mạnh mẽ nhất. 8GB RAM, 256GB ROM.'
        },
        {
            'category': cats['Smartphone'],
            'name': 'Samsung Galaxy S24 Ultra',
            'brand': 'Samsung',
            'price': 29990000,
            'old_price': 33990000,
            'description': 'Galaxy S24 Ultra tích hợp AI thông minh, camera 200MP xuất sắc. 8GB RAM, 256GB ROM.'
        },
        {
            'category': cats['Smartphone'],
            'name': 'Xiaomi 14 Ultra',
            'brand': 'Xiaomi',
            'price': 25990000,
            'description': 'Xiaomi 14 Ultra với ống kính Leica, mang lại trải nghiệm nhiếp ảnh chuyên nghiệp. 16GB RAM, 512GB ROM.'
        },
        {
            'category': cats['Laptop'],
            'name': 'MacBook Air M3',
            'brand': 'Apple',
            'price': 27990000,
            'old_price': 29990000,
            'description': 'MacBook Air với chip M3 hoàn toàn mới, siêu mỏng nhẹ, pin cả ngày. 8GB RAM, 256GB ROM.'
        },
        {
            'category': cats['Laptop'],
            'name': 'ASUS ROG Zephyrus G14',
            'brand': 'Asus',
            'price': 45990000,
            'description': 'Laptop gaming mạnh mẽ và linh hoạt nhất thế giới. 16GB RAM, 512GB ROM.'
        },
        {
            'category': cats['Tai nghe'],
            'name': 'AirPods Pro 2nd Gen',
            'brand': 'Apple',
            'price': 5990000,
            'old_price': 6990000,
            'description': 'Chống ồn chủ động gấp đôi, trải nghiệm âm thanh không gian sống động.'
        },
    ]

    for prod in products_data:
        Product.objects.get_or_create(
            name=prod['name'],
            defaults={
                'category': prod['category'],
                'slug': slugify(prod['name']),
                'brand': prod['brand'],
                'price': prod['price'],
                'old_price': prod.get('old_price'),
                'description': prod['description'],
                'available': True,
                'stock': 10
            }
        )

    print("Successfully seeded categories and products.")

if __name__ == '__main__':
    seed_data()
