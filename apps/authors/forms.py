from django import forms

from apps.news.models import Article


class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ("title", "category", "tags", "summary", "body", "cover", "status")
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Заголовок статьи",
            }),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
            "summary": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 2,
                "placeholder": "Краткое описание (до 300 символов)",
                "maxlength": 300,
            }),
            "body": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 12,
                "placeholder": "Текст статьи",
            }),
            "cover": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
        }
        labels = {
            "title": "Заголовок",
            "category": "Категория",
            "tags": "Теги",
            "summary": "Краткое описание",
            "body": "Текст",
            "cover": "Обложка",
            "status": "Статус",
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        # автор не может публиковать — только черновик / на проверке
        if user and not (user.is_superuser or user.role in {"editor", "admin"}):
            self.fields["status"].choices = [
                (Article.Status.DRAFT, "Черновик"),
                (Article.Status.REVIEW, "На проверке"),
            ]

    def clean_status(self):
        status = self.cleaned_data.get("status")
        user = self.user
        if user and not (user.is_superuser or user.role in {"editor", "admin"}):
            if status not in {Article.Status.DRAFT, Article.Status.REVIEW}:
                raise forms.ValidationError(
                    "Автор может сохранить статью только как «Черновик» или «На проверке»."
                )
        return status