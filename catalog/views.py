from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.forms import HiddenInput
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from catalog.forms import ProductForm
from catalog.mixins import OwnerOrModeratorRequiredMixin
from catalog.models import Contact, Product


class HomeView(TemplateView):
    """Контроллер страницы home с выводом последних 5 продуктов
    и популярными товарами"""

    template_name = "catalog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_products"] = Product.objects.order_by("-created_at")[:5]
        context["popular_products"] = Product.objects.order_by("?")[:4]
        return context


class OurContactsView(TemplateView):
    """Контроллер для отображения контактной информации"""

    template_name = "catalog/contacts.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            contact_data = Contact.objects.first()
        except Contact.DoesNotExist:
            contact_data = None
        context["contact"] = contact_data
        return context


class ContactsView(View):
    """Класс для обработки контактной формы"""

    template_name = "catalog/contacts.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if not all([name, email, message]):
            return render(request, self.template_name, {"error": "Все поля обязательны для заполнения"})
        print(f"Новое сообщение от {name} ({email}): {message}")
        return redirect("contacts_success", name=name)


class ContactsSuccessView(View):
    """Класс для отображения сообщения об успешной отправке формы"""

    def get(self, request, name, *args, **kwargs):
        return HttpResponse(f"Спасибо,{name}! Мы получили Ваше сообщение.")


class CatalogView(ListView):
    """Контроллер для отображения каталога товаров"""

    model = Product
    template_name = "catalog/catalog.html"
    context_object_name = "products"


class ProductListView(ListView):
    model = Product
    template_name = "catalog/product_list.html"
    context_object_name = "products"
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.order_by("name", "created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем информацию о правах пользователя в контекст
        context['can_unpublish'] = self.request.user.has_perm('catalog.can_unpublish_product')
        context['can_delete_any'] = self.request.user.has_perm('catalog.can_delete_any_product')
        context['can_change_publication_status'] = self.request.user.has_perm('catalog.can_change_publication_status')
        return context


class ProductDetailView(DetailView):
    """Контроллер для отображения информации об отдельном товаре"""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Та же фигня, добавляем проверку прав для рендера
        context['can_unpublish'] = self.request.user.has_perm('catalog.can_unpublish_product')
        context['can_delete_any'] = self.request.user.has_perm('catalog.can_delete_any_product')
        context['can_change_publication_status'] = self.request.user.has_perm('catalog.can_change_publication_status')
        return context


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = "/users/login/"
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    success_url = reverse_lazy("product_list")
    permission_required = 'catalog.add_product'
    raise_exception = True

    def form_valid(self, form):
        # Дополнительные действия перед сохранением
        # Автоматически привязываем продукт к текущему пользователю
        form.instance.owner = self.request.user
        # Устанавливаем статус "черновик" для новых продуктов
        form.instance.publication_status = 'draft'
        messages.success(self.request, f'Продукт "{form.instance.name}" создан')
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = "/users/login/"
    model = Product
    form_class = ProductForm
    template_name = "catalog/product_form.html"
    context_object_name = "product"
    permission_required = 'catalog.change_product'
    raise_exception = True

    def get_success_url(self):
        return reverse_lazy("product_detail", kwargs={"pk": self.object.pk})

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Ограничиваем доступ к полю publication_status если нет прав
        if not self.request.user.has_perm('catalog.can_change_publication_status'):
            if 'publication_status' in form.fields:
                form.fields['publication_status'].widget = HiddenInput()
        return form


class ProductDeleteView(LoginRequiredMixin, DeleteView, OwnerOrModeratorRequiredMixin,):
    login_url = "/users/login/"
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")
    context_object_name = "product"

    def __init__(self, **kwargs):
        super().__init__(kwargs)
        self.object = None

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        product_name = self.object.name

        # Проверяем, является ли пользователь владельцем или модератором
        if (self.object.owner != request.user and
                not request.user.has_perm('catalog.can_delete_any_product')):
            messages.error(request, 'У вас нет прав для удаления этого продукта')
            return redirect(success_url)

        self.object.delete()
        messages.success(request, f'Продукт "{product_name}" удален')
        return redirect(success_url)


    def dispatch(self, request, *args, **kwargs):
        # Дополнительная проверка для удаления любого продукта
        if not request.user.has_perm('catalog.can_delete_any_product'):
            raise PermissionDenied("У вас нет прав для удаления продуктов")
        return super().dispatch(request, *args, **kwargs)


class ProductPublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Контроллер для публикации продукта"""
    permission_required = 'catalog.can_change_publication_status'
    raise_exception = True

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.publication_status = 'published'
        product.save()
        messages.success(request, f'Продукт "{product.name}" опубликован')
        return redirect('catalog:product_list')


# Новые контроллеры для специфических действий с продуктами
class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Контроллер для снятия продукта с публикации"""
    login_url = "/users/login/"
    permission_required = 'catalog.can_unpublish_product'
    raise_exception = True

    def post(self, request, pk, *args, **kwargs):
        product = Product.objects.get(pk=pk)

        # Проверяем, может ли пользователь изменять статус публикации
        if not request.user.has_perm('catalog.can_change_publication_status'):
            raise PermissionDenied("У вас нет прав для изменения статуса публикации")

        # Снимаем с публикации
        product.publication_status = 'draft'
        product.is_published = False
        product.save()

        return redirect('product_detail', pk=product.pk)


class MassUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Контроллер для массового снятия товаров с публикации"""
    permission_required = 'catalog.can_unpublish_product'
    raise_exception = True

    def post(self, request):
        # Снимаем с публикации все опубликованные товары
        published_products = Product.objects.filter(publication_status='published')
        count = published_products.count()

        if count > 0:
            published_products.update(publication_status='draft')
            messages.success(request, f'Снято с публикации: {count} товаров')
        else:
            messages.info(request, 'Нет товаров для снятия с публикации')

        return redirect('catalog:product_list')


class ProductModerationListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    """Контроллер для страницы модерации продуктов"""
    login_url = "/users/login/"
    model = Product
    template_name = "catalog/product_moderation.html"
    context_object_name = "products"
    permission_required = 'catalog.can_unpublish_product'
    raise_exception = True

    def get_queryset(self):
        # Показываем только продукты, требующие модерации
        return Product.objects.filter(publication_status__in=['pending', 'published'])


# Миксин для проверки прав модератора
class ProductModeratorMixin(LoginRequiredMixin):
    """Миксин для проверки прав модератора продуктов"""

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.has_perm('catalog.can_unpublish_product') or
                request.user.has_perm('catalog.can_delete_any_product') or
                request.user.has_perm('catalog.can_change_publication_status')):
            raise PermissionDenied("У вас нет прав модератора продуктов")
        return super().dispatch(request, *args, **kwargs)


class ProductModerationDashboard(ProductModeratorMixin, TemplateView):
    """Панель управления модератора"""
    template_name = "catalog/moderation_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_products'] = Product.objects.filter(publication_status='pending')
        context['published_products'] = Product.objects.filter(publication_status='published')
        context['can_unpublish'] = self.request.user.has_perm('catalog.can_unpublish_product')
        context['can_delete_any'] = self.request.user.has_perm('catalog.can_delete_any_product')
        context['can_change_status'] = self.request.user.has_perm('catalog.can_change_publication_status')
        return context


class ProductChangeStatusView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """Контроллер для изменения статуса продукта"""
    permission_required = 'catalog.can_change_publication_status'
    raise_exception = True

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        new_status = request.POST.get('status')
        if new_status in dict(Product.PUBLICATION_STATUS).keys():
            product.publication_status = new_status
            product.save()
            messages.success(request, f'Статус продукта "{product.name}" изменен')
        return redirect('catalog:product_list')
