from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView
from catalog.models import Contact, Product


class HomeView(TemplateView):
    """Контроллер страницы home с выводом последних 5 продуктов
       и популярными товарами"""
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["latest_products"] = Product.objects.order_by("-created_at")[:5]
        context["popular_products"] = Product.objects.order_by("?")[:4]
        return context


class OurContactsView(TemplateView):
    """Контроллер для отображения контактной информации"""
    template_name = "contacts.html"
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
    template_name = "contacts.html"

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
    template_name = "catalog.html"
    context_object_name = "products"

class ProductDetailView(DetailView):
    """Контроллер для отображения информации об отдельном товаре"""
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"
