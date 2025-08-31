from django.contrib import messages
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q, Avg
from django.forms import HiddenInput
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from catalog.forms import ProductForm
from catalog.mixins import OwnerOrModeratorRequiredMixin
from catalog.models import Contact, Product, Category


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
        return Product.objects.filter(
            publication_status='published',
            is_published=True
        ).select_related('category', 'owner').order_by("name", "created_at")

    def get_context_data(self, **kwargs):
        cache_key = f"product_list_context_{self.request.user.pk if self.request.user.is_authenticated else 'anon'}"
        cached_context = cache.get(cache_key)

        if cached_context is None:
            context = super().get_context_data(**kwargs)

            # Кэшируем вычисления
            cacheable_context = {
                'total_products_count': Product.objects.filter(
                    publication_status='published', is_published=True
                ).count(),
            }

            cache.set(cache_key, cacheable_context, 60 * 30)

            # Добавляем данные в контекст
            context.update(cacheable_context)
            context.update({
                'can_unpublish': self.request.user.has_perm('catalog.can_unpublish_product'),
                'can_delete_any': self.request.user.has_perm('catalog.can_delete_any_product'),
                'can_change_publication_status': self.request.user.has_perm('catalog.can_change_publication_status'),
                'categories': Category.objects.annotate(
                    product_count=Count('products', filter=Q(products__publication_status='published'))
                ).filter(product_count__gt=0).order_by('name'),
            })

            return context

        # Если есть кэш, обновляем контекст
        context = super().get_context_data(**kwargs)
        context.update(cached_context)
        context.update({
            'can_unpublish': self.request.user.has_perm('catalog.can_unpublish_product'),
            'can_delete_any': self.request.user.has_perm('catalog.can_delete_any_product'),
            'can_change_publication_status': self.request.user.has_perm('catalog.can_change_publication_status'),
            'categories': Category.objects.annotate(
                product_count=Count('products', filter=Q(products__publication_status='published'))
            ).filter(product_count__gt=0).order_by('name'),
        })

        return context


class ProductDetailView(DetailView):
    """Контроллер для отображения информации об отдельном товаре"""

    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_context_data(self, **kwargs):
        # Генерируем уникальный ключ для кеша контекста
        cache_key = f"product_context_{self.object.pk}_{self.request.user.pk if self.request.user.is_authenticated else 'anon'}"

        # Пытаемся получить контекст из кеша
        cached_data = cache.get(cache_key)
        if cached_data is None:
            # Это типа если нет кэша, то создаём новый контекст
            context = super().get_context_data(**kwargs)
            cacheable_data = {
                'can_unpublish': self.request.user.has_perm('catalog.can_unpublish_product'),
                'can_delete_any': self.request.user.has_perm('catalog.can_delete_any_product'),
                'can_change_publication_status': self.request.user.has_perm('catalog.can_change_publication_status'),
            }
            # Сохраняем в кеш на 15 минут
            cache.set(cache_key, cacheable_data, 60 * 15)
        else:
            # Используем данные из кеша
            context = super().get_context_data(**kwargs)
            context.update(cached_data)

            # Добавляем проверку прав (они всегда должны быть свежими)
        context['can_unpublish'] = self.request.user.has_perm('catalog.can_unpublish_product')
        context['can_delete_any'] = self.request.user.has_perm('catalog.can_delete_any_product')
        context['can_change_publication_status'] = self.request.user.has_perm('catalog.can_change_publication_status')
        return context

    def get_object(self, queryset=None):
        # Кеширование объекта продукта
        pk = self.kwargs.get('pk')
        cache_key = f"product_{pk}"

        product = cache.get(cache_key)
        if product is None:
            product = super().get_object(queryset)
            # Кешируем продукт на 1 час
            cache.set(cache_key, product, 60 * 60)

        return product


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


class ProductDeleteView(LoginRequiredMixin, OwnerOrModeratorRequiredMixin,  DeleteView,):
    login_url = "/users/login/"
    model = Product
    template_name = "catalog/product_confirm_delete.html"
    success_url = reverse_lazy("product_list")
    context_object_name = "product"


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


class CategoryProductsView(ListView):
    """
    Контроллер для отображения продуктов по конкретной категории
    """
    template_name = "catalog/category_products.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self, min_price=None, max_price=None):
        category_slug = self.kwargs['category_slug']
        try:
            category = Category.objects.get(slug=category_slug)
            products = Product.objects.filter(
                category=category,
                publication_status='published',
                is_published=True
            ).select_related('category', 'owner')

            # Добавить фильтрацию и сортировку
            filters = self.get_filters()
            if filters.get('in_stock') == 'true':
                products = products.filter(in_stock=True)

            if min_price:
                products = products.filter(price__gte=min_price)
            if max_price:
                products = products.filter(price__lte=max_price)

            sort_by = filters.get('sort_by', 'name')
            if sort_by == 'price_asc':
                products = products.order_by('price')
            elif sort_by == 'price_desc':
                products = products.order_by('-price')
            elif sort_by == 'newest':
                products = products.order_by('-created_at')
            else:
                products = products.order_by('name')

            return products

        except Category.DoesNotExist:
            return Product.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = self.kwargs.get('category_slug')

        try:
            category = Category.objects.get(slug=category_slug)

            # Получаем отфильтрованный queryset для статистики
            filtered_products = self.get_queryset()

            # Статистика
            stats = {
                'total_products': Product.objects.filter(
                    category=category,
                    publication_status='published',
                    is_published=True
                ).count(),
                'published_products': Product.objects.filter(
                    category=category,
                    publication_status='published',
                    is_published=True
                ).count(),
                'available_products': Product.objects.filter(
                    category=category,
                    publication_status='published',
                    is_published=True,
                    in_stock=True
                ).count(),
                'avg_price': Product.objects.filter(
                    category=category,
                    publication_status='published',
                    is_published=True
                ).aggregate(avg=Avg('price'))['avg'] or 0
            }
            context.update({
                'category': category,
                'total_count': self.get_queryset().count(),
                'filtered_count': filtered_products.count(),
                'filters': self.get_filters(),
                'stats': stats
            })
            context.update(self.get_permission_context())

        except Category.DoesNotExist:
            context.update({
                'category': None,
                'total_count': 0,
                'filtered_count': 0,
                'filters': {},
                'stats': None
            })

        return context

    def get_filters(self):
        """
        Извлечение параметров фильтрации из запроса
        """
        filters = {}
        filter_params = ['in_stock', 'sort_by',  'min_price', 'max_price']

        for param in filter_params:
            value = self.request.GET.get(param)
            if value:
                filters[param] = value

        return filters

    def get_permission_context(self):
        """
        Контекст с правами пользователя
        """
        return {
            'can_unpublish': self.request.user.has_perm('catalog.can_unpublish_product'),
            'can_delete_any': self.request.user.has_perm('catalog.can_delete_any_product'),
            'can_change_publication_status': self.request.user.has_perm('catalog.can_change_publication_status'),
        }


class CategoryProductsSearchView(ListView):
    """
    Контроллер для поиска товаров по ВСЕМ категориям
    """
    template_name = "catalog/category_products_search.html"
    context_object_name = "products"
    paginate_by = 12

    def get_queryset(self):
        search_term = self.request.GET.get('search', '').strip()

        if not search_term:
            return Product.objects.none()

        # Поиск по всем опубликованным товарам
        products = Product.objects.filter(
            publication_status='published',
            is_published=True
        ).filter(
            Q(name__icontains=search_term) |
            Q(description__icontains=search_term) |
            Q(category__name__icontains=search_term) |
            Q(brand__icontains=search_term)
        ).select_related('category').order_by('name')

        return products

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_term = self.request.GET.get('search', '')

        context.update({
            'search_term': search_term,
            'total_results': self.get_queryset().count(),
            'categories': Category.objects.annotate(
                product_count=Count('products', filter=Q(products__publication_status='published'))
            ).filter(product_count__gt=0)
        })

        return context


class CategoryListView(LoginRequiredMixin, ListView):
    """
    Контроллер для отображения всех категорий
    """
    model = Category
    template_name = 'catalog/categories.html'
    context_object_name = 'categories'
    paginate_by = 12
    login_url = '/users/login/'

    def get_queryset(self):
        """
        Возвращает queryset категорий
        """
        return Category.objects.annotate(
            product_count=Count('products', filter=Q(products__publication_status='published'))
        ).exclude(slug__isnull=True).exclude(slug='').order_by('name')

    def get_context_data(self, **kwargs):
        """
        Контекст для шаблона
        """
        context = super().get_context_data(**kwargs)

        # Статистика
        context['total_products'] = Product.objects.filter(
            publication_status='published'
        ).count()

        context['published_products'] = Product.objects.filter(
            publication_status='published',
            is_published=True
        ).count()

        context['available_products'] = Product.objects.filter(
            publication_status='published',
            in_stock=True,
            stock__gt=0
        ).count()

        # Добавляем информацию о категориях без slug (для админов)
        if self.request.user.is_staff:
            context['categories_without_slug'] = Category.objects.filter(
                Q(slug__isnull=True) | Q(slug='')
            )

        return context


class CategoryAdminListView(LoginRequiredMixin, ListView):
    """
    Контроллер для администрирования категорий
    (только для staff пользователей)
    """
    model = Category
    template_name = 'catalog/categories_admin.html'
    context_object_name = 'categories'
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        """
        Проверка прав доступа
        """
        if not request.user.is_staff:
            from django.core.exceptions import PermissionDenied
            raise PermissionDenied("Доступ только для администраторов")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """
        Полный список категорий для администрирования
        """
        return Category.objects.annotate(
            total_products=Count('products'),
            published_products=Count('products', filter=Q(products__publication_status='published')),
            draft_products=Count('products', filter=Q(products__publication_status='draft'))
        ).order_by('name')

    def get_context_data(self, **kwargs):
        """
        Контекст для админ-панели категорий
        """
        context = super().get_context_data(**kwargs)
        context['is_admin_view'] = True
        return context
