from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from catalog.models import Contact, Product


def home(request):
    """Контроллер страницы home с выводом последних 5 продуктов"""

    # Получаем 5 последних добавленных товаров
    latest_products = Product.objects.order_by("-created_at")[:5]

    # Получаем популярные товары
    popular_products = Product.objects.order_by("?")[:4]

    context = {
        "latest_products": latest_products,
        "popular_products": popular_products,
    }
    return render(request, "home.html", context)


def our_contacts(request):
    try:
        contact_data = Contact.objects.first()
    except Contact.DoesNotExist:
        contact_data = None

    context = {"contact": contact_data}
    return render(request, "contacts.html", context)


def contacts(request):
    """Контроллер страницы contacts. Есть обработка POST-запроса с выводом ответного
    сообщения через redirect"""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if not all([name, email, message]):
            return render(request, "contacts.html", {"error": "Все поля обязательны для заполнения"})
        print(f"Новое сообщение от {name} ({email}): {message}")
        return redirect("contacts_success", name=name)
    return render(request, "contacts.html")


def contacts_success(request, name):
    return HttpResponse(f"Спасибо,{name}! Мы получили Ваше сообщение.")


def catalog(request):
    products = Product.objects.all()
    context = {"products": products}
    return render(request, "catalog.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    return render(request, "product_detail.html", {"product": product})
