import random

from django.core.management.base import BaseCommand
from django.utils import timezone

from catalog.models import Category, Product


class Command(BaseCommand):
    help = "Очищает базу и добавляет тестовые продукты"

    def handle(self, *args, **options):
        # Удаляем все существующие данные
        self.stdout.write("Удаление старых данных...")
        Product.objects.all().delete()
        Category.objects.all().delete()

        # Создаем тестовые категории
        categories = ["Казявочничество", "Болтогонятельство", "Фигассе", "Хрень отдельная", "Фигня без масла"]

        created_categories = []
        for cat_name in categories:
            category = Category.objects.create(name=cat_name, description=f"Описание категории {cat_name}")
            created_categories.append(category)
            self.stdout.write(f"Создана категория: {cat_name}")

        # Создаем тестовые продукты
        products_data = [
            {"name": "Казабер", "price": 29999.99},
            {"name": "Буква зю", "price": 59999.99},
            {"name": "Ёперный театр", "price": 1999.99},
            {"name": "Кракозябра", "price": 3999.99},
            {"name": "Птица обломинго", "price": 1499.99},
            {"name": "Хренатоида", "price": 99.99},
            {"name": "Бурагозень", "price": 2999.99},
        ]

        for product_data in products_data:
            product = Product.objects.create(
                name=product_data["name"],
                description=f"Отличный {product_data['name']} по выгодной цене",
                category=random.choice(created_categories),
                price=product_data["price"],
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            self.stdout.write(f"Создан продукт: {product.name} ({product.price} руб.)")

        self.stdout.write(self.style.SUCCESS("Тестовые данные успешно добавлены!"))
