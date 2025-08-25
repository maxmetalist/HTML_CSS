from django.core.management.base import BaseCommand
from catalog.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Устанавливает владельцев для существующих продуктов'

    def handle(self, *args, **options):
        # Находим первого пользователя (обычно админа)
        default_owner = User.objects.first()

        if not default_owner:
            self.stdout.write(self.style.ERROR('Нет пользователей в системе'))
            return

        # Устанавливаем владельца для всех продуктов
        products_without_owner = Product.objects.filter(owner__isnull=True)
        count = products_without_owner.count()

        if count > 0:
            products_without_owner.update(owner=default_owner)
            self.stdout.write(
                self.style.SUCCESS(f'Установлен владелец для {count} продуктов')
            )
        else:
            self.stdout.write(self.style.SUCCESS('Все продукты уже имеют владельца'))
