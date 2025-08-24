from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse

from blog import models
from blog.forms import BlogPostForm
from blog.mixins import BlogPublishPermissionMixin
from blog.models import BlogPost
from django.core.mail import send_mail
from django.conf import settings


class BlogPostListView(ListView):
    """Контроллер для отображения списка всех блог-записей"""

    model = BlogPost
    template_name = "blog/blogpost_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Фильтрация только опубликованных статей"""
        queryset = BlogPost.objects.all()

        # 1. Суперпользователь видит ВСЕ
        if self.request.user.is_superuser:
            return queryset.order_by('-created_at')

        # 2. Контент-менеджеры видят ВСЕ
        if self.request.user.has_perm('blog.can_edit_all_blogposts'):
            return queryset.order_by('-created_at')

        # 3. Для авторизованных пользователей - опубликованные + свои записи
        if self.request.user.is_authenticated:
            return queryset.filter(
                models.Q(is_published=True) |
                models.Q(author=self.request.user)
            ).order_by('-created_at')

        return queryset.filter(is_published=True).order_by("-created_at")


class BlogPostDetailView(DetailView):
    """Контроллер для детального просмотра блог-записи"""

    model = BlogPost
    template_name = "blog/blogpost_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = super().get_queryset()

        # Для обычных юзеров показываем только опубликованные посты
        if not self.request.user.has_perm('blog.can_edit_all_blogposts'):
            queryset = queryset.filter(is_published=True)

        return queryset

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


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    """Контроллер для создания записи (применяется отложенное создание url)"""

    model = BlogPost
    form_class = BlogPostForm
    template_name = "blog/blogpost_form.html"
    fields = ["title", "content", "preview", "is_published"]
    success_url = reverse_lazy("blog:post_list")

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, 'Запись блога создана')
        return super().form_valid(form)


class BlogPostUpdateView(UpdateView):
    """Контроллер для редактирования записи"""

    model = BlogPost
    template_name = "blog/blogpost_form.html"
    fields = ["title", "content", "preview", "is_published"]

    def get_success_url(self):
        """Перенаправление на просмотр статьи после редактирования"""
        return reverse("blog:post_detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        # Обычные юзеры не могут менять статус
        if not self.request.user.has_perm('blog.can_change_blog_status'):
            if 'status' in form.fields:
                form.fields['status'].widget.attrs['disabled'] = True
                form.fields['status'].help_text = 'Изменение статуса доступно только контент-менеджерам'

        return form

    def form_valid(self, form):
        messages.success(self.request, 'Запись блога обновлена')
        return super().form_valid(form)


class BlogPostDeleteView(DeleteView):
    """Контроллер для удаления записи"""

    model = BlogPost
    template_name = "blog/blogpost_confirm_delete.html"
    success_url = reverse_lazy("blog:post_list")
    context_object_name = 'post'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Запись блога удалена')
        return super().delete(request, *args, **kwargs)


class BlogPostPublishView(LoginRequiredMixin, BlogPublishPermissionMixin, UpdateView):
    """Контроллер для публикации записи"""
    model = BlogPost
    fields = []
    template_name = 'blog/blogpost_publish.html'

    def form_valid(self, form):
        form.instance.status = 'published'
        messages.success(self.request, 'Запись опубликована')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail', kwargs={'pk': self.object.pk})


class BlogPostUnpublishView(LoginRequiredMixin, View):
    """View для снятия с публикации"""

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)

        if not request.user.has_perm('blog.can_publish_blogpost'):
            messages.error(request, 'У вас нет прав для снятия записей с публикации')
            return redirect('blog:post_detail', pk=post.pk)

        post.status = 'draft'
        post.save()
        messages.success(request, 'Запись снята с публикации')

        return redirect('blog:post_detail', pk=post.pk)


class BlogPostChangeStatusView(LoginRequiredMixin, View):
    """View для изменения статуса записи блога"""

    def post(self, request, pk):
        post = get_object_or_404(BlogPost, pk=pk)

        # Проверка прав - только контент-менеджеры
        if not request.user.has_perm('blog.can_change_blog_status'):
            messages.error(request, 'У вас нет прав для изменения статуса записей')
            return redirect('blog:post_detail', pk=post.pk)

        new_status = request.POST.get('status')

        if new_status in dict(BlogPost.STATUS_CHOICES).keys():
            post.status = new_status
            post.save()
            messages.success(request, f'Статус записи изменен на "{post.get_status_display()}"')
        else:
            messages.error(request, 'Неверный статус')

        return redirect('blog:post_detail', pk=post.pk)


class MyBlogPostsView(LoginRequiredMixin, ListView):
    """Контроллер для отображения записей текущего пользователя"""
    model = BlogPost
    template_name = 'blog/my_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return BlogPost.objects.filter(author=self.request.user).order_by('-created_at')
