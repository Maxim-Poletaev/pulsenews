from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Ваш комментарий...",
                "maxlength": 2000,
            }),
        }
        labels = {
            "text": "",
        }

    def clean_text(self):
        text = self.cleaned_data.get("text", "").strip()
        if len(text) < 3:
            raise forms.ValidationError("Комментарий слишком короткий (минимум 3 символа).")
        if len(text) > 2000:
            raise forms.ValidationError("Комментарий слишком длинный (максимум 2000 символов).")
        return text