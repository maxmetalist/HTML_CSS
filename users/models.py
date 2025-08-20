from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    # Делаем email уникальным идентификатором вместо username
    username = None
    email = models.EmailField(_("email address"), unique=True)

    # Дополнительные поля (аватарка, телефон, страна)
    avatar = models.ImageField(_("avatar"), upload_to="users/avatars/", blank=True, null=True)
    phone_number = PhoneNumberField(
        _("phone number"), blank=True, null=True, region=None, help_text=_("Example: +79771234567")
    )
    country = models.CharField(_("country"), max_length=100, blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.email
