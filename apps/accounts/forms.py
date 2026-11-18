from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import User


class LoginForm(AuthenticationForm):
    """Стандартная форма входа, но с Bootstrap-классами."""
    username = forms.CharField(
        label="Логин",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Логин",
            "autofocus": True,
        }),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Пароль",
        }),
    )


class RegisterForm(UserCreationForm):
    """Регистрация читателя. Роль всегда reader."""
    email = forms.EmailField(
        label="Email",
        required=False,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
        }),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Логин",
                "autofocus": True,
            }),
        }
        labels = {
            "username": "Логин",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # пароли — стандартные поля UserCreationForm, добавим классы
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Пароль",
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Повторите пароль",
        })
        self.fields["password1"].label = "Пароль"
        self.fields["password2"].label = "Повторите пароль"

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.READER          # все новые — читатели
        if commit:
            user.save()
        return user