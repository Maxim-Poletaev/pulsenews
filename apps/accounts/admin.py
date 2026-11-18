from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "avatar_preview", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")

    fieldsets = UserAdmin.fieldsets + (
        ("Профиль PulseNews", {"fields": ("role", "bio", "avatar")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Профиль PulseNews", {"fields": ("role",)}),
    )

    @admin.display(description="Аватар")
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:32px;border-radius:50%;" />',
                obj.avatar.url,
            )
        return "—"

    # ─── Ограничение: только суперюзер видит пользователей ───
    def has_module_permission(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# Group — скрываем для всех, кроме суперюзера
admin.site.unregister(Group)


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        return request.user.is_superuser