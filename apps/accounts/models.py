from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        READER = "reader", "Читатель"
        AUTHOR = "author", "Автор"
        EDITOR = "editor", "Редактор"
        ADMIN = "admin", "Администратор"

    role = models.CharField(
        "роль",
        max_length=10,
        choices=Role.choices,
        default=Role.READER,
    )
    bio = models.TextField("о себе", blank=True)
    avatar = models.ImageField("аватар", upload_to="avatars/", blank=True)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.username

    # ─── Проверки ролей ──────────────────────────────
    @property
    def is_reader(self) -> bool:
        return self.role == self.Role.READER

    @property
    def is_author_role(self) -> bool:
        return self.role in {self.Role.AUTHOR, self.Role.EDITOR, self.Role.ADMIN}

    @property
    def is_editor(self) -> bool:
        return self.role in {self.Role.EDITOR, self.Role.ADMIN}

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN