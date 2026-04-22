import os
import django
import random
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Category, Product

def create_sample_products():
    categories = {
        'Smartphone': Category.objects.get(id=1),
        'Laptop': Category.objects.get(id=2),
        'Máy tính bảng': Category.objects.get(id=3),
        'Đồng hồ thông minh': Category.objects.get(id=4),
        'Tai nghe': Category.objects.get(id=5),
    }

    products_data = [
        # Laptops
        {
            'category': categories['Laptop'],
            'name': 'MacBook Pro 14 inch M3 Pro',
            'brand': 'Apple',
            'price': 49990000,
            'old_price': 54990000,
            'description': 'MacBook Pro mới với chip M3 Pro, màn hình Liquid Retina XDR 14 inch cực đẹp.',
            'is_hotdeal': True
        },
        {
            'category': categories['Laptop'],
            'name': 'Dell XPS 15 9530',
            'brand': 'Dell',
            'price': 42500000,
            'old_price': 45000000,
            'description': 'Laptop Dell cao cấp nhất, màn hình OLED 3.5K, Core i7-13700H.',
            'is_hotdeal': False
        },
        {
            'category': categories['Laptop'],
            'name': 'Asus ROG Strix G16 2024',
            'brand': 'Asus',
            'price': 38990000,
            'old_price': 41990000,
            'description': 'Laptop Gaming mạnh mẽ với RTX 4060, màn hình 165Hz.',
            'is_hotdeal': True
        },
        
        # Smartphones
        {
            'category': categories['Smartphone'],
            'name': 'iPhone 15 Pro Max 256GB',
            'brand': 'Apple',
            'price': 30990000,
            'old_price': 34990000,
            'description': 'Siêu phẩm mới nhất từ Apple với khung viền Titan và chip A17 Pro.',
            'is_hotdeal': True
        },
        {
            'category': categories['Smartphone'],
            'name': 'Samsung Galaxy S24 Ultra',
            'brand': 'Samsung',
            'price': 28990000,
            'old_price': 33990000,
            'description': 'Flagship đỉnh cao của Samsung với bút S-Pen và tính năng AI mới nhất.',
            'is_hotdeal': True
        },
        {
            'category': categories['Smartphone'],
            'name': 'Xiaomi 14 Pro 5G',
            'brand': 'Xiaomi',
            'price': 18500000,
            'old_price': 21000000,
            'description': 'Điện thoại Xiaomi mới nhất với camera Leica siêu nét.',
            'is_hotdeal': False
        },
        
        # Tablets
        {
            'category': categories['Máy tính bảng'],
            'name': 'iPad Pro M2 11 inch Wi-Fi',
            'brand': 'Apple',
            'price': 21990000,
            'old_price': 23990000,
            'description': 'iPad mạnh mẽ nhất với chip M2, màn hình 120Hz mượt mà.',
            'is_hotdeal': False
        },
        {
            'category': categories['Máy tính bảng'],
            'name': 'Samsung Galaxy Tab S9 Ultra',
            'brand': 'Samsung',
            'price': 24500000,
            'old_price': 27000000,
            'description': 'Máy tính bảng màn hình lớn 14.6 inch, kháng nước IP68.',
            'is_hotdeal': True
        },
        
        # Smartwatches
        {
            'category': categories['Đồng hồ thông minh'],
            'name': 'Apple Watch Ultra 2',
            'brand': 'Apple',
            'price': 19990000,
            'old_price': 21990000,
            'description': 'Đồng hồ thể thao chuyên nghiệp với thời lượng pin ấn tượng.',
            'is_hotdeal': True
        },
        {
            'category': categories['Đồng hồ thông minh'],
            'name': 'Samsung Galaxy Watch 6 Classic',
            'brand': 'Samsung',
            'price': 7500000,
            'old_price': 8990000,
            'description': 'Thiết kế cổ điển với vòng xoay bezel vật lý.',
            'is_hotdeal': False
        },
        
        # Audio
        {
            'category': categories['Tai nghe'],
            'name': 'Sony WH-1000XM5',
            'brand': 'Sony',
            'price': 7990000,
            'old_price': 9490000,
            'description': 'Tai nghe chống ồn tốt nhất thế giới hiện nay.',
            'is_hotdeal': True
        },
        {
            'category': categories['Tai nghe'],
            'name': 'AirPods Pro 2 USB-C',
            'brand': 'Apple',
            'price': 5490000,
            'old_price': 6190000,
            'description': 'Tai nghe True Wireless cao cấp từ Apple với sạc USB-C.',
            'is_hotdeal': False
        }
    ]

    for data in products_data:
        p, created = Product.objects.get_or_create(
            name=data['name'],
            defaults={
                'category': data['category'],
                'brand': data['brand'],
                'price': Decimal(data['price']),
                'old_price': Decimal(data['old_price']) if data.get('old_price') else None,
                'description': data['description'],
                'is_hotdeal': data.get('is_hotdeal', False),
                'stock': random.randint(10, 50),
                'available': True
            }
        )
        if created:
            print(f"Created product: {p.name}")
        else:
            print(f"Product already exists: {p.name}")

if __name__ == '__main__':
    create_sample_products()
