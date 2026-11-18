from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.core.models import TimeStampedModel


# ─────────────────────────────────────────────
# Менеджер: только опубликованные и уже наступившие
# ─────────────────────────────────────────────
class PublishedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            status=Article.Status.PUBLISHED,
            published_at__lte=timezone.now(),
        )


# ─────────────────────────────────────────────
# Категория
# ─────────────────────────────────────────────
class Category(models.Model):
    name = models.CharField("название", max_length=60, unique=True)
    slug = models.SlugField("слаг", unique=True, blank=True)
    description = models.TextField("описание", blank=True)

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "категории"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────
# Тег
# ─────────────────────────────────────────────
class Tag(models.Model):
    name = models.CharField("название", max_length=40, unique=True)
    slug = models.SlugField("слаг", unique=True, blank=True)

    class Meta:
        verbose_name = "тег"
        verbose_name_plural = "теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)


# ─────────────────────────────────────────────
# Статья
# ─────────────────────────────────────────────
class Article(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT     = "draft",     "Черновик"
        REVIEW    = "review",    "На проверке"
        PUBLISHED = "published", "Опубликовано"
        ARCHIVED  = "archived",  "В архиве"

    title = models.CharField("заголовок", max_length=200)
    slug = models.SlugField("слаг", unique=True, blank=True, max_length=220)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name="автор",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
        verbose_name="категория",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="articles",
        verbose_name="теги",
    )
    summary = models.CharField("краткое описание", max_length=300)
    body = models.TextField("текст")
    cover = models.ImageField("обложка", upload_to="covers/%Y/%m/", blank=True)
    status = models.CharField(
        "статус",
        max_length=10,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    published_at = models.DateTimeField("опубликовано", null=True, blank=True)
    views = models.PositiveIntegerField("просмотры", default=0)
    is_featured = models.BooleanField("на главной", default=False)

    # менеджеры
    objects = models.Manager()          # по умолчанию
    published = PublishedManager()      # только опубликованные

    class Meta:
        verbose_name = "статья"
        verbose_name_plural = "статьи"
        ordering = ["-published_at", "-created_at"]
        indexes = [
            models.Index(fields=["status", "-published_at"]),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 1) slug
        if not self.slug:
            base = slugify(self.title, allow_unicode=True)[:200] or "article"
            slug, i = base, 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{i}"
                i += 1
            self.slug = slug

        # 2) published_at
        if self.status == self.Status.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("news:article_detail", kwargs={"slug": self.slug})


# ─────────────────────────────────────────────
# Комментарий
# ─────────────────────────────────────────────
class Comment(TimeStampedModel):
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="статья",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="автор",
    )
    text = models.TextField("текст")
    is_approved = models.BooleanField("одобрен", default=False)

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"
        ordering = ["created_at"]

    def __str__(self):
        return f"Комментарий от {self.author} к «{self.article}»"