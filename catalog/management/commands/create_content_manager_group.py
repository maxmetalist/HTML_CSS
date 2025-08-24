from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from blog.models import BlogPost


class Command(BaseCommand):
    help = 'Создает группу контент-менеджеров с правами управления блогом'

    def handle(self, *args, **options):
        # Получаем content type для модели BlogPost
        content_type = ContentType.objects.get_for_model(BlogPost)

        # Получаем необходимые разрешения для блога
        blog_permissions = Permission.objects.filter(
            content_type=content_type,
            codename__in=[
                'add_blogpost', 'change_blogpost', 'delete_blogpost',
                'can_publish_blogpost', 'can_edit_all_blogposts',
                'can_delete_all_blogposts', 'can_change_blog_status'
            ]
        )

        # Создаем группу "Контент-менеджер"
        content_manager_group, created = Group.objects.get_or_create(
            name='Контент-менеджер'
        )

        # Добавляем разрешения к группе
        content_manager_group.permissions.set(blog_permissions)

        if created:
            self.stdout.write(
                self.style.SUCCESS('Группа "Контент-менеджер" успешно создана')
            )
        else:
            # Убедимся, что у группы есть все необходимые права
            current_permissions = content_manager_group.permissions.all()
            for perm in blog_permissions:
                if perm not in current_permissions:
                    content_manager_group.permissions.add(perm)

            self.stdout.write(
                self.style.WARNING('Группа "Контент-менеджер" уже существует, права обновлены')
            )

        self.stdout.write(
            self.style.SUCCESS(f'Добавлено {blog_permissions.count()} прав к группе')
        )