from django.db.models import F
from django.views.generic import DetailView, ListView
from apps.core.pagination import ElidedPaginator
from .models import Article, Category, Comment, Tag
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from .forms import CommentForm

class TagListView(ListView):
    model = Article
    template_name = "news/article_list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        self.tag = Tag.objects.filter(slug=self.kwargs["slug"]).first()
        if not self.tag:
            return Article.published.none()
        return (
            Article.published
            .filter(tags=self.tag)
            .select_related("category", "author")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tag"] = self.tag
        return ctx

class HomeView(ListView):
    """Главная: featured + последние статьи."""
    model = Article
    template_name = "news/home.html"
    context_object_name = "articles"
    paginate_by = 6

    def get_queryset(self):
        return Article.published.select_related("category", "author")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured"] = (
            Article.published
            .filter(is_featured=True)
            .select_related("category", "author")[:2]
        )
        return ctx


class ArticleListView(ListView):
    """Все новости: полная лента с сортировкой."""
    model = Article
    template_name = "news/article_list.html"
    context_object_name = "articles"
    paginate_by = 9
    paginator_class = ElidedPaginator

    def get_queryset(self):
        qs = Article.published.select_related("category", "author")
        sort = self.request.GET.get("sort", "new")
        if sort == "views":
            qs = qs.order_by("-views", "-published_at")
        elif sort == "old":
            qs = qs.order_by("published_at")
        else:
            qs = qs.order_by("-published_at", "-created_at")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_sort"] = self.request.GET.get("sort", "new")
        return ctx


class ArticleDetailView(DetailView):
    model = Article
    template_name = "news/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        return (
            Article.published
            .select_related("category", "author")
            .prefetch_related("tags")
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        Article.objects.filter(pk=obj.pk).update(views=F("views") + 1)
        obj.refresh_from_db(fields=["views"])
        return obj

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        article = self.object

        ctx["comments"] = (
            article.comments
            .filter(is_approved=True)
            .select_related("author")
            .order_by("created_at")
        )

        if article.category_id:
            ctx["related"] = (
                Article.published
                .filter(category_id=article.category_id)
                .exclude(pk=article.pk)
                .select_related("category", "author")[:3]
            )
        else:
            ctx["related"] = Article.published.none()

        ctx["comment_form"] = CommentForm()
        return ctx


class CategoryListView(ListView):
    model = Article
    template_name = "news/article_list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        self.category = Category.objects.filter(slug=self.kwargs["slug"]).first()
        if not self.category:
            return Article.published.none()
        return (
            Article.published
            .filter(category=self.category)
            .select_related("category", "author")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["category"] = self.category
        return ctx


class SearchView(ListView):
    model = Article
    template_name = "news/article_list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return Article.published.none()
        return (
            Article.published
            .filter(title__icontains=q) | Article.published.filter(summary__icontains=q)
        ).select_related("category", "author")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "").strip()
        return ctx

@login_required
@require_POST
def comment_create(request, slug):
    article = get_object_or_404(Article.published, slug=slug)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.is_approved = False
        comment.save()
        messages.success(
            request,
            "Комментарий отправлен на модерацию. Он появится после проверки редактором.",
        )
    else:
        messages.error(request, "Не удалось отправить комментарий. Проверьте текст.")

    return redirect(article.get_absolute_url())