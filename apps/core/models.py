from django.db import models


class TimeStampedModel(models.Model):
    """
    Абстрактная базовая модель: добавляет created_at / updated_at.
    Наследники получают поля автоматически, своей таблицы у модели нет.
    """
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at"]