from django.urls import path
from django.views.generic import TemplateView
from . import views


app_name = "news"

urlpatterns = [
    path("", views.HomeView.as_view(), name="home"),
    path("news/", views.ArticleListView.as_view(), name="article_list"),
    path("news/<str:slug>/", views.ArticleDetailView.as_view(), name="article_detail"),
    path("category/<str:slug>/", views.CategoryListView.as_view(), name="category"),
    path("search/", views.SearchView.as_view(), name="search"),
    path("tag/<str:slug>/", views.TagListView.as_view(), name="tag"),
    path("news/<str:slug>/comment/", views.comment_create, name="comment_create"),
    path("about/", TemplateView.as_view(template_name="news/about.html"), name="about"),
    path("demo/seed/", views.DemoSeedView.as_view(), name="demo_seed"),
    path("demo/seed/run/", views.demo_seed_run, name="demo_seed_run"),
]