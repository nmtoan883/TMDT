from django.core.management.base import BaseCommand
from django.utils.text import slugify

from core.models import Category, Product


class Command(BaseCommand):
    help = "Seed sample categories/products for search suggestion testing."

    def handle(self, *args, **options):
        categories_data = [
            {"name": "Smartphone", "icon": "fa-mobile-alt"},
            {"name": "Laptop", "icon": "fa-laptop"},
            {"name": "May tinh bang", "icon": "fa-tablet-alt"},
            {"name": "Dong ho thong minh", "icon": "fa-clock-o"},
            {"name": "Tai nghe", "icon": "fa-headphones"},
            {"name": "Phu kien", "icon": "fa-plug"},
        ]

        category_map = {}
        for item in categories_data:
            category, _ = Category.objects.get_or_create(
                name=item["name"],
                defaults={
                    "slug": slugify(item["name"]),
                    "icon": item["icon"],
                },
            )
            category_map[item["name"]] = category

        products_data = [
            {
                "name": "iPhone 15 Pro Max 256GB",
                "category": "Smartphone",
                "brand": "Apple",
                "price": 34990000,
                "old_price": 36990000,
                "description": "iPhone flagship chip A17 Pro, camera zoom tot.",
                "stock": 20,
                "available": True,
            },
            {
                "name": "Samsung Galaxy S24 Ultra",
                "category": "Smartphone",
                "brand": "Samsung",
                "price": 29990000,
                "old_price": 33990000,
                "description": "AI phone, camera 200MP, pin ben bi.",
                "stock": 18,
                "available": True,
            },
            {
                "name": "Xiaomi 14 Ultra Leica",
                "category": "Smartphone",
                "brand": "Xiaomi",
                "price": 25990000,
                "old_price": 27990000,
                "description": "Camera Leica, hieu nang cao.",
                "stock": 16,
                "available": True,
            },
            {
                "name": "OPPO Find X7",
                "category": "Smartphone",
                "brand": "OPPO",
                "price": 20990000,
                "old_price": 22990000,
                "description": "Man hinh dep, sac nhanh.",
                "stock": 14,
                "available": True,
            },
            {
                "name": "MacBook Air M3 13 inch",
                "category": "Laptop",
                "brand": "Apple",
                "price": 27990000,
                "old_price": 29990000,
                "description": "Laptop mong nhe, pin lau.",
                "stock": 12,
                "available": True,
            },
            {
                "name": "ASUS ROG Zephyrus G14",
                "category": "Laptop",
                "brand": "Asus",
                "price": 45990000,
                "old_price": 48990000,
                "description": "Laptop gaming cao cap.",
                "stock": 8,
                "available": True,
            },
            {
                "name": "Dell XPS 13 Plus",
                "category": "Laptop",
                "brand": "Dell",
                "price": 35990000,
                "old_price": 38990000,
                "description": "Ultrabook thiet ke dep, man hinh chat luong cao.",
                "stock": 9,
                "available": True,
            },
            {
                "name": "AirPods Pro 2nd Gen",
                "category": "Tai nghe",
                "brand": "Apple",
                "price": 5990000,
                "old_price": 6990000,
                "description": "Tai nghe chong on chu dong.",
                "stock": 25,
                "available": True,
            },
            {
                "name": "Sony WH-1000XM5",
                "category": "Tai nghe",
                "brand": "Sony",
                "price": 8990000,
                "old_price": 9990000,
                "description": "Tai nghe over-ear chong on tot.",
                "stock": 11,
                "available": True,
            },
            {
                "name": "Apple Watch Series 9",
                "category": "Dong ho thong minh",
                "brand": "Apple",
                "price": 10990000,
                "old_price": 11990000,
                "description": "Dong ho thong minh theo doi suc khoe.",
                "stock": 13,
                "available": True,
            },
        ]

        created_count = 0
        updated_count = 0
        for item in products_data:
            category = category_map[item["category"]]
            defaults = {
                "category": category,
                "slug": slugify(item["name"]),
                "brand": item["brand"],
                "price": item["price"],
                "old_price": item["old_price"],
                "description": item["description"],
                "stock": item["stock"],
                "available": item["available"],
            }
            product, created = Product.objects.get_or_create(
                name=item["name"],
                defaults=defaults,
            )
            if created:
                created_count += 1
            else:
                changed = False
                for key, value in defaults.items():
                    if getattr(product, key) != value:
                        setattr(product, key, value)
                        changed = True
                if changed:
                    product.save()
                    updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed done: created {created_count}, updated {updated_count} products."
            )
        )
