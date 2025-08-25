from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class BlogPost(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Черновик'),
        ('published', 'Опубликовано'),
        ('archived', 'В архиве'),
    ]

    objects = None
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержимое")
    slug = models.SlugField(unique=True, max_length=200, verbose_name='URL-адрес')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    preview = models.ImageField(upload_to="blog_previews/", verbose_name="Превью", blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='Дата публикации')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name='Статус')
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    views_count = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")

    def get_absolute_url(self):
        return reverse("blog:post_detail", kwargs={"pk": self.pk})

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Автоматическая синхронизация is_published со статусом
        if self.status == 'published':
            self.is_published = True
            if not self.published_at:
                self.published_at = timezone.now()
        else:
            self.is_published = False
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Запись блога"
        verbose_name_plural = "Записи блога"
        permissions = [
            ("can_publish_blogpost", "Может публиковать записи блога"),
            ("can_edit_all_blogposts", "Может редактировать все записи блога"),
            ("can_delete_all_blogposts", "Может удалять все записи блога"),
            ("can_change_blog_status", "Может изменять статус записей блога"),
        ]
