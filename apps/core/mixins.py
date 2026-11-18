from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class AuthorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """
    Пускает только авторизованных с ролью author / editor / admin.
    Иначе — 403 (или редирект на логин, если не авторизован).
    """
    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in {
            "author", "editor", "admin",
        }

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()   # редирект на логин
        raise PermissionDenied("У вас нет прав для доступа в кабинет автора.")


class OwnerOrEditorMixin:
    """
    Для UpdateView / DeleteView: автор может трогать только свои статьи,
    редактор и админ — любые.
    Ожидает, что у объекта есть поле `author`.
    """
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user
        if user.is_superuser or user.role in {"editor", "admin"}:
            return super().dispatch(request, *args, **kwargs)
        if obj.author_id == user.id:
            return super().dispatch(request, *args, **kwargs)
        raise PermissionDenied("Это не ваша статья.")