from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product


class Command(BaseCommand):
    help = 'Создает группы и назначает разрешения'

    def handle(self, *args, **options):
        # Тут мы создаем группу "Модератор продуктов"
        moderator_group, created = Group.objects.get_or_create(
            name='Модератор продуктов'
        )

        # Тут мы получаем разрешения
        content_type = ContentType.objects.get_for_model(Product)

        # Разрешение на отмену публикации
        unpublish_permission = Permission.objects.get(
            codename='can_unpublish_product',
            content_type=content_type
        )

        # Разрешение на удаление любого продукта
        delete_permission = Permission.objects.get(
            codename='delete_product',
            content_type=content_type
        )

        # Разрешение на изменение статуса публикации
        change_status_permission = Permission.objects.get(
            codename='can_change_publication_status',
            content_type=content_type
        )

        # И добавляем наши кастомные разрешения в группу модераторов
        moderator_group.permissions.add(
            unpublish_permission,
            delete_permission,
            change_status_permission
        )
        # Это просто вывод сообщения о создании группы
        self.stdout.write(
            self.style.SUCCESS('Группа "Модератор продуктов" создана и настроена')
        )
