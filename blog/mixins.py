from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin


class ContentManagerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав контент-менеджера"""

    def test_func(self):
        user = self.request.user
        return (user.has_perm('blog.can_publish_blogpost') or
                user.has_perm('blog.can_edit_all_blogposts') or
                user.has_perm('blog.can_delete_all_blogposts') or
                user.has_perm('blog.can_change_blog_status'))

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для управления контентом блога")


class BlogEditPermissionMixin(UserPassesTestMixin):
    """Миксин для проверки прав редактирования конкретной записи"""

    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        # Автор может редактировать свои записи
        if obj.author == user:
            return True

        # Контент-менеджеры могут редактировать все записи
        return user.has_perm('blog.can_edit_all_blogposts')

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для редактирования этой записи")


class BlogDeletePermissionMixin(UserPassesTestMixin):
    """Миксин для проверки прав удаления конкретной записи"""

    def test_func(self):
        obj = self.get_object()
        user = self.request.user

        # Автор может удалять свои записи
        if obj.author == user:
            return True

        # Контент-менеджеры могут удалять все записи
        return user.has_perm('blog.can_delete_all_blogposts')

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для удаления этой записи")


class BlogPublishPermissionMixin(UserPassesTestMixin):
    """Миксин для проверки прав публикации"""

    def test_func(self):
        return self.request.user.has_perm('blog.can_publish_blogpost')

    def handle_no_permission(self):
        raise PermissionDenied("У вас нет прав для публикации записей")