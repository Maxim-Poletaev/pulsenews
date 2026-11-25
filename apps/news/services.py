from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import Article, Category, Tag, Comment

User = get_user_model()


TEST_USERS = [
    {"username": "admin",   "password": "Admin2026!",   "role": "admin",   "is_staff": True,  "is_superuser": True,  "first_name": "Админ",  "last_name": "Системный"},
    {"username": "editor",  "password": "Editor2026!",  "role": "editor",  "is_staff": True,  "is_superuser": False, "first_name": "Ольга",  "last_name": "Редакторова"},
    {"username": "author",  "password": "Author2026!",  "role": "author",  "is_staff": True,  "is_superuser": False, "first_name": "Пётр",   "last_name": "Петров"},
    {"username": "author2", "password": "Author2026!",  "role": "author",  "is_staff": False, "is_superuser": False, "first_name": "Анна",   "last_name": "Сидорова"},
    {"username": "reader",  "password": "Reader2026!",  "role": "reader",  "is_staff": False, "is_superuser": False, "first_name": "Иван",   "last_name": "Читатель"},
]


def seed_users():
    """Создаёт/обновляет тестовых пользователей. Возвращает (created, updated)."""
    created, updated = 0, 0
    for data in TEST_USERS:
        password = data.pop("password")
        username = data["username"]
        user, is_created = User.objects.get_or_create(username=username, defaults=data)
        if is_created:
            created += 1
        else:
            for k, v in data.items():
                setattr(user, k, v)
            updated += 1
        user.set_password(password)   # всегда переустанавливаем пароль
        user.save()
        data["password"] = password   # вернём обратно, чтобы TEST_USERS не мутировал
    return created, updated


def seed_articles():
    """Создаёт категории, теги и статьи. Возвращает (articles_created, comments_created)."""
    # Категории
    categories = {}
    for name, desc in [
        ("Политика", "Внутренняя и внешняя политика"),
        ("Технологии", "IT, гаджеты, наука"),
        ("Спорт", "Спортивные события"),
        ("Культура", "Искусство, кино, музыка"),
    ]:
        cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
        categories[name] = cat

    # Теги
    tags = {}
    for name in ["Выборы", "IT", "Футбол", "Выставка", "Кино", "Нейросети", "Олимпиада", "Театр"]:
        tag, _ = Tag.objects.get_or_create(name=name)
        tags[name] = tag

    admin = User.objects.get(username="admin")
    editor = User.objects.get(username="editor")
    author = User.objects.get(username="author")
    author2 = User.objects.get(username="author2")
    now = timezone.now()

    articles_data = [
        ("Правительство объявило о новых мерах поддержки IT-отрасли", "Политика", admin, "published", 1, "Пакет льгот затронет разработчиков и стартапы.", ["IT", "Выборы"], True),
        ("Открытие нового технопарка в регионе", "Технологии", editor, "published", 2, "Площадка объединит 40 резидентов.", ["IT", "Нейросети"], False),
        ("Сборная вышла в финал чемпионата", "Спорт", author, "published", 3, "Решающий матч завершился со счётом 2:1.", ["Футбол", "Олимпиада"], True),
        ("Выставка современного искусства открылась", "Культура", author2, "published", 4, "Более 80 работ молодых художников.", ["Выставка", "Театр"], False),
        ("Нейросети научились предсказывать погоду", "Технологии", author, "published", 5, "Модель обучена на данных за 50 лет.", ["Нейросети", "IT"], False),
        ("Премьера нового фильма собрала рекордную кассу", "Культура", author2, "published", 7, "За первый уикенд — более 500 млн рублей.", ["Кино"], False),
        ("Черновик: обзор нового гаджета", "Технологии", author, "draft", None, "Готовится подробный обзор.", ["IT"], False),
        ("На проверке: интервью с тренером сборной", "Спорт", author, "review", None, "Материал готов, ждёт редактуры.", ["Футбол"], False),
        ("Архив: прошлогодняя выставка", "Культура", author2, "archived", 300, "Событие прошло в прошлом году.", ["Выставка"], False),
        ("На проверке: аналитика выборов", "Политика", editor, "review", None, "Аналитический материал готовится.", ["Выборы"], False),
    ]

    articles_created = 0
    for title, cat_name, user, status, days_ago, summary, tag_names, featured in articles_data:
        # идемпотентность: пропускаем, если статья с таким заголовком уже есть
        if Article.objects.filter(title=title).exists():
            continue
        published_at = now - timedelta(days=days_ago) if days_ago is not None else None
        article = Article.objects.create(
            title=title,
            author=user,
            category=categories[cat_name],
            summary=summary,
            body=summary + " Подробности в полном тексте статьи.",
            status=status,
            published_at=published_at,
            is_featured=featured,
        )
        article.tags.set([tags[t] for t in tag_names])
        articles_created += 1

    # Комментарии — только к опубликованным, только если их ещё нет
    comments_created = 0
    published = Article.objects.filter(status=Article.Status.PUBLISHED)
    if published.exists() and not Comment.objects.exists():
        texts = [
            "Отличная новость!",
            "Спасибо за подробный разбор.",
            "Не согласен с автором, но интересно.",
            "Когда будет продолжение?",
            "Очень полезно, спасибо редакции.",
        ]
        readers = list(User.objects.filter(username__in=["reader", "author2", "editor"]))
        for i, text in enumerate(texts):
            Comment.objects.create(
                article=published[i % published.count()],
                author=readers[i % len(readers)],
                text=text,
                is_approved=(i % 2 == 0),
            )
            comments_created += 1

    return articles_created, comments_created