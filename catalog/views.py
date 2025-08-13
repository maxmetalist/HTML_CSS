from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView, TemplateView, CreateView, UpdateView, DeleteView

from catalog.forms import ProductForm
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
    template_name = 'catalog/product_list.html'
    context_object_name = 'products'
    paginate_by = 10

    def get_queryset(self):
        return Product.objects.order_by('name', 'created_at')


class ProductDetailView(DetailView):
    """Контроллер для отображения информации об отдельном товаре"""
    model = Product
    template_name = "catalog/product_detail.html"
    context_object_name = "product"


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('product_list')

    def form_valid(self, form):
        # Дополнительные действия перед сохранением
        return super().form_valid(form)

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    context_object_name = 'product'

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'pk': self.object.pk})

class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('product_list')
    context_object_name = 'product'
