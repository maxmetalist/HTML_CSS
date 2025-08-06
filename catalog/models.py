from django.db import models


class Category(models.Model):
    """Модель категории товаров"""

    objects = None
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

    objects = None
    name = models.CharField(max_length=200, verbose_name="Наименование")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    image = models.ImageField(upload_to="catalog/photos", verbose_name="Изображение", blank=True, null=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, verbose_name="Категория", blank=True, null=True, related_name="products"
    )
    in_stock = models.BooleanField(default=True, verbose_name="В наличии")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    brand = models.CharField(max_length=100, blank=True, null=True, verbose_name="Бренд")
    weight = models.FloatField(blank=True, null=True, verbose_name="Вес (кг)")
    dimensions = models.CharField(max_length=50, blank=True, null=True, verbose_name="Размеры")
    material = models.CharField(max_length=100, blank=True, null=True, verbose_name="Материал")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за покупку")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Старая цена")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата последнего изменения")

    class Meta:
        verbose_name = "товар"
        verbose_name_plural = "товары"
        ordering = ["name", "created_at"]

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="catalog/photos")

    def __str__(self):
        return f"Изображение для {self.product.name}"


class Contact(models.Model):
    """Модель для хранения контактных данных"""

    DoesNotExist = None
    objects = None
    address = models.CharField("Адрес", max_length=200)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email")
    schedule = models.TextField("График работы")
    map_code = models.TextField("Код карты", blank=True, help_text="HTML-код карты (iframe)")

    class Meta:
        verbose_name = "контакт"
        verbose_name_plural = "контакты"

    def __init__(self, *args, **kwargs):
        super().__init__(args, kwargs)
        self.id = None

    def __str__(self):
        return f"Контактные данные ({self.id})"
