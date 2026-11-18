from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.core.mixins import AuthorRequiredMixin, OwnerOrEditorMixin
from apps.news.models import Article

from .forms import ArticleForm


class MyArticleListView(AuthorRequiredMixin, ListView):
    model = Article
    template_name = "authors/article_list.html"
    context_object_name = "articles"
    paginate_by = 12

    def get_queryset(self):
        qs = Article.objects.select_related("category", "author")
        user = self.request.user
        if user.is_superuser or user.role in {"editor", "admin"}:
            return qs
        return qs.filter(author=user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        ctx["is_editor"] = user.is_superuser or user.role in {"editor", "admin"}
        return ctx


class ArticleCreateView(AuthorRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm
    template_name = "authors/article_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, f"Статья «{form.instance.title}» сохранена.")
        return response

    def get_success_url(self):
        return reverse_lazy("authors:my_articles")


class ArticleUpdateView(AuthorRequiredMixin, OwnerOrEditorMixin, UpdateView):
    model = Article
    form_class = ArticleForm
    template_name = "authors/article_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Статья «{form.instance.title}» обновлена.")
        return response

    def get_success_url(self):
        return reverse_lazy("authors:my_articles")


class ArticleDeleteView(AuthorRequiredMixin, OwnerOrEditorMixin, DeleteView):
    model = Article
    template_name = "authors/article_confirm_delete.html"
    success_url = reverse_lazy("authors:my_articles")

    def form_valid(self, form):
        title = self.object.title
        response = super().form_valid(form)
        messages.info(self.request, f"Статья «{title}» удалена.")
        return response