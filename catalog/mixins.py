from django.core.exceptions import PermissionDenied
from django.contrib.auth.mixins import UserPassesTestMixin


class OwnerRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является владельцем объекта"""

    def test_func(self):
        obj = self.get_object()
        return obj.owner == self.request.user

    def handle_no_permission(self):
        if self.request.user.has_perm('catalog.can_delete_any_product'):
            # Модераторам разрешаем доступ
            return True
        raise PermissionDenied("У вас нет прав для выполнения этого действия")


class OwnerOrModeratorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки, что пользователь является владельцем или модератором"""

    def test_func(self):
        obj = self.get_object()
        # Владелец или модератор с правом удаления
        return (obj.owner == self.request.user or
                self.request.user.has_perm('catalog.can_delete_any_product'))
