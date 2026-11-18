from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import Category, Tag, Article, Comment


# ─────────────────────────────────────────────
# Inline-комментарии внутри статьи
# (без @admin.register — это не отдельный раздел)
# ─────────────────────────────────────────────
class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ("author", "text", "is_approved", "created_at")
    readonly_fields = ("created_at",)
    raw_id_fields = ("author",)
    can_delete = True
    show_change_link = True


# ─────────────────────────────────────────────
# Категория
# ─────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ─────────────────────────────────────────────
# Тег
# ─────────────────────────────────────────────
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


# ─────────────────────────────────────────────
# Статья
# ─────────────────────────────────────────────
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = (
        "cover_preview", "title", "category", "author",
        "status", "published_at", "views", "comments_count",
        "is_featured",
    )
    list_filter = ("status", "category", "is_featured", "tags", "author")
    search_fields = ("title", "summary", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    raw_id_fields = ("author",)
    filter_horizontal = ("tags",)
    list_editable = ("status", "is_featured")
    readonly_fields = (
        "views", "published_at", "created_at", "updated_at",
        "cover_preview_large",
    )
    inlines = [CommentInline]
    actions = ("publish", "archive", "back_to_draft")
    fieldsets = (
        ("Основное", {
            "fields": ("title", "slug", "author", "category", "tags"),
        }),
        ("Содержание", {
            "fields": ("summary", "body", "cover_preview_large", "cover"),
        }),
        ("Публикация", {
            "fields": ("status", "is_featured", "published_at"),
        }),
        ("Служебное", {
            "fields": ("views", "created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    # ─── Колонки в списке ───
    @admin.display(description="Обложка")
    def cover_preview(self, obj):
        if obj.cover:
            return format_html(
                '<img src="{}" style="height:40px;border-radius:4px;" />',
                obj.cover.url,
            )
        return "—"

    @admin.display(description="Обложка")
    def cover_preview_large(self, obj):
        if obj and obj.cover:
            return format_html(
                '<img src="{}" style="max-height:200px;border-radius:6px;" />',
                obj.cover.url,
            )
        return "Обложка не загружена"

    @admin.display(description="Комментарии")
    def comments_count(self, obj):
        return obj.comments.count()

    # ─── Ограничение по ролям ───
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user

        if user.is_superuser:
            return qs
        if user.role == "editor":
            return qs
        if user.role == "author":
            return qs.filter(author=user)
        return qs.none()

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.role in {"author", "editor"}

    def has_change_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or user.role == "editor":
            return True
        if user.role == "author" and obj is not None and obj.author_id == user.id:
            return True
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if user.is_superuser or user.role == "editor":
            return True
        if user.role == "author" and obj is not None and obj.author_id == user.id:
            return True
        return False

    def save_model(self, request, obj, form, change):
        if not change and request.user.role == "author":
            obj.author = request.user
        super().save_model(request, obj, form, change)

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        if request.user.role == "author" and not request.user.is_superuser:
            readonly.append("is_featured")
        return readonly

    def formfield_for_choice_field(self, db_field, request, **kwargs):
        if (
            db_field.name == "status"
            and request.user.role == "author"
            and not request.user.is_superuser
        ):
            kwargs["choices"] = [
                (Article.Status.DRAFT, "Черновик"),
                (Article.Status.REVIEW, "На проверке"),
            ]
        return super().formfield_for_choice_field(db_field, request, **kwargs)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if not (request.user.is_superuser or request.user.role == "editor"):
            actions.pop("publish", None)
            actions.pop("archive", None)
        return actions

    # ─── Массовые действия ───
    @admin.action(description="Опубликовать выбранные")
    def publish(self, request, queryset):
        count = 0
        for article in queryset:
            if article.status != Article.Status.PUBLISHED:
                article.status = Article.Status.PUBLISHED
                article.published_at = article.published_at or timezone.now()
                article.save()
                count += 1
        self.message_user(request, f"Опубликовано: {count}")

    @admin.action(description="Отправить в архив")
    def archive(self, request, queryset):
        updated = queryset.update(status=Article.Status.ARCHIVED)
        self.message_user(request, f"В архив: {updated}")

    @admin.action(description="Вернуть в черновики")
    def back_to_draft(self, request, queryset):
        updated = queryset.update(status=Article.Status.DRAFT)
        self.message_user(request, f"Черновиков: {updated}")


# ─────────────────────────────────────────────
# Комментарий (отдельный раздел для модерации)
# ─────────────────────────────────────────────
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("article", "author", "is_approved", "created_at", "short_text")
    list_filter = ("is_approved",)
    search_fields = ("text", "article__title", "author__username")
    raw_id_fields = ("article", "author")
    actions = ("approve", "unapprove")

    @admin.display(description="Текст")
    def short_text(self, obj):
        return obj.text[:60] + ("…" if len(obj.text) > 60 else "")

    @admin.action(description="Одобрить комментарии")
    def approve(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f"Одобрено: {updated}")

    @admin.action(description="Снять одобрение")
    def unapprove(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f"Снято одобрение: {updated}")