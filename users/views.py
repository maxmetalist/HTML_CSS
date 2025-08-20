from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from config import settings
from .forms import RegisterForm, LoginForm, UserProfileForm
from .models import User


class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = "users/register.html"
    success_url = reverse_lazy("catalog:home")

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save()

        # Автоматический вход после регистрации
        login(self.request, user)

        # Отправка приветственного письма
        self.send_welcome_email(user)

        return response

    def send_welcome_email(self, user):
        try:
            subject = _("Ну что, бобро поржаловать в наш магаз!")
            from_email = settings.DEFAULT_FROM_EMAIL
            message = _(
                f"Здорово! {user.email},\n\n"
                "Спасибо, что выбираешь наш магаз!"
                "Надеюсь те тут понравится и ты найдёшь себе какую_нибудь хрень по душе...\n\n"
                "Всего тебе самого самого,\n"
                "Команда магаза, то есть Масяма.\n"
                "Возникнут вопросы, пиши не стесняйся.\n"
            ).format(user=user)

            send_mail(
                subject=subject,
                message= message,
                from_email=from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Ошибка отправки email: {e}")


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "users/login.html"

    def get_success_url(self):
        return reverse_lazy("home")


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"
    login_url = "/users/login/"


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile")

    def get_object(self, queryset=None):
        return self.request.user
