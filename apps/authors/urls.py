from django.urls import path

from . import views


app_name = "authors"

urlpatterns = [
    path("", views.MyArticleListView.as_view(), name="my_articles"),
    path("articles/new/", views.ArticleCreateView.as_view(), name="article_create"),
    path("articles/<str:slug>/edit/", views.ArticleUpdateView.as_view(), name="article_edit"),
    path("articles/<str:slug>/delete/", views.ArticleDeleteView.as_view(), name="article_delete"),
]