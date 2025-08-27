from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Product, Category


def get_products_by_category(category_slug, user=None, include_unpublished=False):
    """
    Сервисная функция для получения всех продуктов в указанной категории
    с учетом прав доступа и статуса публикации
    """
    try:
        # Получаем категорию по slug
        category = Category.objects.get(slug=category_slug)

        # Базовый запрос
        queryset = Product.objects.filter(category=category)

        # Фильтрация по статусу публикации
        if not include_unpublished:
            # Для анонимных пользователей - только опубликованные
            if user is None or not user.is_authenticated:
                queryset = queryset.filter(publication_status='published', is_published=True)
            else:
                # Для авторизованных пользователей
                if user.has_perm('catalog.can_change_publication_status'):
                    # Модераторы видят все продукты
                    pass
                else:
                    # Обычные пользователи видят опубликованные + свои продукты
                    queryset = queryset.filter(
                        Q(publication_status='published', is_published=True) |
                        Q(owner=user)
                    )

        # Оптимизация запроса
        products = queryset.select_related('category', 'owner').prefetch_related('images')

        return {
            'category': category,
            'products': products,
            'total_count': products.count()
        }

    except Category.DoesNotExist:
        return None


def get_category_products_with_filters(category_slug, filters=None, user=None):
    """
    Расширенная версия с фильтрацией и сортировкой
    """
    result = get_products_by_category(category_slug, user)

    if not result:
        return None

    products = result['products']

    # Применяем фильтры
    if filters:
        # Фильтр по наличию
        if filters.get('in_stock') == 'true':
            products = products.filter(in_stock=True)

        # Фильтр по цене
        min_price = filters.get('min_price')
        max_price = filters.get('max_price')
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)

        # Фильтр по бренду
        brand = filters.get('brand')
        if brand:
            products = products.filter(brand__icontains=brand)

    # Сортировка
    sort_by = filters.get('sort_by', 'name')
    if sort_by == 'price_asc':
        products = products.order_by('price')
    elif sort_by == 'price_desc':
        products = products.order_by('-price')
    elif sort_by == 'newest':
        products = products.order_by('-created_at')
    elif sort_by == 'name':
        products = products.order_by('name')

    result['products'] = products
    result['filtered_count'] = products.count()

    return result


def get_category_products_paginated(category_slug, page_number=1, per_page=12, user=None, filters=None):
    """
    Версия с пагинацией и фильтрацией
    """
    result = get_category_products_with_filters(category_slug, filters, user)

    if not result:
        return None

    paginator = Paginator(result['products'], per_page)

    try:
        products_page = paginator.page(page_number)
    except (PageNotAnInteger, EmptyPage):
        products_page = paginator.page(1)

    return {
        'category': result['category'],
        'products_page': products_page,
        'total_count': result['total_count'],
        'filtered_count': result.get('filtered_count', result['total_count']),
        'filters': filters or {}
    }


def get_category_stats(category_slug):
    """
    Получение статистики по категории
    """
    try:
        category = Category.objects.get(slug=category_slug)

        stats = {
            'total_products': Product.objects.filter(category=category).count(),
            'published_products': Product.objects.filter(
                category=category,
                publication_status='published',
                is_published=True
            ).count(),
            'available_products': Product.objects.filter(
                category=category,
                in_stock=True,
                stock__gt=0
            ).count(),
            'avg_price': Product.objects.filter(
                category=category,
                publication_status='published'
            ).aggregate(avg_price=models.Avg('price'))['avg_price'] or 0,
            'brands': Product.objects.filter(
                category=category,
                publication_status='published'
            ).exclude(brand__isnull=True).exclude(brand='').values_list('brand', flat=True).distinct()
        }

        return {
            'category': category,
            'stats': stats
        }

    except Category.DoesNotExist:
        return None
