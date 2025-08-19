from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email", "autocomplete": "email"}
        ),
    )
    password1 = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль", "autocomplete": "new-password"}
        ),
    )
    password2 = forms.CharField(
        label=_("Подтверждение пароля"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Подтвердите пароль", "autocomplete": "new-password"}
        ),
    )

    class Meta:
        model = User
        fields = ("email", "password1", "password2")


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите ваш email", "autocomplete": "email"}
        ),
    )
    password = forms.CharField(
        label=_("Пароль"),
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Введите пароль", "autocomplete": "current-password"}
        ),
    )

    error_messages = {
        "invalid_login": _("А чё мыло такое корявое, а мож пароль. Заведи ка заново по-нормальному."),
        "inactive": _("Этот акк походу неактивен."),
    }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone_number", "country", "avatar"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите имя"}),
            "last_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите фамилию"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Введите email"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "+79123456789"}),
            "country": forms.TextInput(attrs={"class": "form-control", "placeholder": "Введите страну"}),
        }
