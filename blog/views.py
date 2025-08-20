from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from blog.models import BlogPost
from django.core.mail import send_mail
from django.conf import settings


class BlogPostListView(ListView):
    """Контроллер для отображения списка всех блог-записей"""

    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"
    paginate_by = 5

    def get_queryset(self):
        """Фильтрация только опубликованных статей"""
        return BlogPost.objects.filter(is_published=True).order_by("-created_at")


class BlogPostDetailView(DetailView):
    """Контроллер для детального просмотра блог-записи"""

    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        """Увеличение счетчика просмотров и проверка на 100 просмотров"""
        obj = super().get_object(queryset)
        obj.views_count += 1
        obj.save()

        # Отправка письма при достижении 100 просмотров
        if obj.views_count == 100:
            self.send_congratulation_email(obj)

        return obj

    def send_congratulation_email(self, post):
        """Отправка письма с поздравлением"""
        subject = f'Поздравляю! Статья "{post.title}" достигла 100 просмотров! Возьми с полки пирожок!'
        message = (
            f'Статья "{post.title}" достигла 100 просмотров!\n\n'
            f"Ссылка на статью: {self.request.build_absolute_uri(post.get_absolute_url())}\n"
            f"Текущее количество просмотров: {post.views_count}"
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["z.max82@mail.ru"],
            fail_silently=True,
        )


class BlogPostCreateView(CreateView):
    """Контроллер для создания записи (применяется отложенное создание url)"""

    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ["title", "content", "preview", "is_published"]
    success_url = reverse_lazy("blog:post_list")


class BlogPostUpdateView(UpdateView):
    """Контроллер для редактирования записи"""

    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ["title", "content", "preview", "is_published"]

    def get_success_url(self):
        """Перенаправление на просмотр статьи после редактирования"""
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})


class BlogPostDeleteView(DeleteView):
    """Контроллер для удаления записи"""

    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")
