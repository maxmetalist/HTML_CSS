from django.db import models


class Category(models.Model):
    """Модель категории товаров"""

    name = models.CharField(max_length=100, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель товара"""

    name = models.CharField(max_length=100, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    image = models.ImageField(upload_to="catalog/photos", verbose_name="Изображение", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, verbose_name="Категория", blank=True, null=True, related_name="products"
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за покупку")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["name", "created_at"]

    def __str__(self):
        return self.name
