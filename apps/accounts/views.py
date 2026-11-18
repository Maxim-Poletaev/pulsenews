from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, RegisterForm


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True       # если уже залогинен — сразу на главную

    def form_valid(self, form):
        messages.success(self.request, f"Добро пожаловать, {form.get_user().username}!")
        return super().form_valid(form)


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy("news:home")

    def post(self, request, *args, **kwargs):
        messages.info(request, "Вы вышли из системы.")
        return super().post(request, *args, **kwargs)


def register(request):
    if request.user.is_authenticated:
        return redirect("news:home")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Аккаунт создан. Добро пожаловать, {user.username}!")
            return redirect("news:home")
        messages.error(request, "Проверьте форму — есть ошибки.")
    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})