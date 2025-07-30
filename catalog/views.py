from django.http import HttpResponse
from django.shortcuts import redirect, render

from catalog.models import Contact, Product


def home(request):
    """Контроллер страницы home с выводом последних 5 продуктов"""
    latest_products = Product.objects.order_by("-created_at")[:5]

    # Выводим в консоль информацию о продуктах
    print("\nПоследние 5 добавленных продуктов:")
    for product in latest_products:
        print(
            f"ID: {product.id}, Название: {product.name}, Цена: {product.price}, "
            f"Категория: {product.category.name if product.category else 'Нет категории'}, "
            f"Дата создания: {product.created_at}"
        )

    return render(request, "home.html", {"latest_products": latest_products})


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
    return render(request, "catalog.html")
