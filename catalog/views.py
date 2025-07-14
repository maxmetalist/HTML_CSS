from django.shortcuts import render, redirect
from django.http import HttpResponse


def home(request):
    """Контроллер страницы home"""
    return render(request, "home.html")

def contacts(request):
    """Контроллер страницы contacts. Есть обработка POST-запроса с выводом ответного
       сообщения через redirect"""
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if not all([name, email, message]):
            return render(request, "contacts.html",
                          {'error':'Все поля обязательны для заполнения'})
        print(f"Новое сообщение от {name} ({email}): {message}")
        return redirect("contacts_success", name=name)
    return render(request, "contacts.html")

def contacts_success(request, name):
    return HttpResponse(f"Спасибо,{name}! Мы получили Ваше сообщение.")

def catalog(request):
    return render(request, "catalog.html")
