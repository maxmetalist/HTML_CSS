import os

from django import forms
from django.core.exceptions import ValidationError

from .models import Product

FORBIDDEN_WORDS = ["казино", "криптовалюта", "крипта", "биржа", "дешево", "бесплатно", "обман", "полиция", "радар"]


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "created_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "updated_at": forms.DateTimeInput(attrs={"type": "datetime-local"}),
        }
        labels = {
            'publication_status': 'Статус публикации',
            'is_published': 'Опубликовано',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Скрываем поле publication_status по умолчанию
        if 'publication_status' in self.fields:
            self.fields['publication_status'].widget = forms.HiddenInput()

        # Общая стилизация для всех полей
        for field_name, field in self.fields.items():
            if field_name in ["in_stock"]:
                continue

            field.widget.attrs.update({"class": "form-control", "placeholder": f"Введите {field.label.lower()}"})

        self.fields["image"].widget.attrs.update({"class": "form-control", "accept": "image/jpeg, image/png"})

    def clean_name(self):
        name = self.cleaned_data["name"].lower()
        for word in FORBIDDEN_WORDS:
            if word in name:
                raise forms.ValidationError(f"Название содержит запрещенное слово: {word}")
        return self.cleaned_data["name"]

    def clean_description(self):
        description = self.cleaned_data.get("description", "").lower()
        if description:
            for word in FORBIDDEN_WORDS:
                if word in description:
                    raise forms.ValidationError(f"Описание содержит запрещенное слово: {word}")
        return self.cleaned_data.get("description")

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price < 0:
            raise forms.ValidationError("Цена не может быть отрицательной")
        return price

    def clean_image(self):
        image = self.cleaned_data.get("image")

        if not image:
            return image

        # Проверка размера файла (5 МБ)
        max_size = 5 * 1024 * 1024  # 5 Мегов
        if image.size > max_size:
            raise ValidationError("Размер файла не должен превышать 5 МБ.")

        # Проверка формата файла
        valid_extensions = [".jpg", ".jpeg", ".png"]
        ext = os.path.splitext(image.name)[1].lower()
        if ext not in valid_extensions:
            raise ValidationError("Поддерживаются только файлы JPEG и PNG.")
