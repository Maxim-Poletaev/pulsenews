import os
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "signal_1.settings")

import django
django.setup()


import random
from datetime import timedelta
from django.utils import timezone
from apps.accounts.models import User
from apps.news.models import Category, Tag, Article, Comment


def run():
    print("─── Очистка старых данных ───")
    Comment.objects.all().delete()
    Article.objects.all().delete()
    Tag.objects.all().delete()
    Category.objects.all().delete()
    # Пользователей не трогаем — они нужны для входа
    print("Готово\n")

    print("─── Пользователи ───")
    users = {}
    users["admin"] = User.objects.filter(username="admin").first() or User.objects.create_superuser(
        username="admin", email="admin@pulsenews.local", password="Admin2026!",
        role=User.Role.ADMIN,
    )
    users["editor"], _ = User.objects.get_or_create(
        username="editor",
        defaults=dict(
            email="editor@pulsenews.local", role=User.Role.EDITOR,
            is_staff=True, first_name="Ольга", last_name="Редакторова",
        ),
    )
    users["editor"].set_password("Editor2026!")
    users["editor"].is_staff = True
    users["editor"].save()

    users["author"], _ = User.objects.get_or_create(
        username="author",
        defaults=dict(
            email="author@pulsenews.local", role=User.Role.AUTHOR,
            is_staff=True, first_name="Пётр", last_name="Петров",
        ),
    )
    users["author"].set_password("Author2026!")
    users["author"].is_staff = True
    users["author"].save()

    users["author2"], _ = User.objects.get_or_create(
        username="author2",
        defaults=dict(
            email="author2@pulsenews.local", role=User.Role.AUTHOR,
            first_name="Анна", last_name="Сидорова",
        ),
    )
    users["author2"].set_password("Author2026!")
    users["author2"].save()

    users["reader"], _ = User.objects.get_or_create(
        username="reader",
        defaults=dict(
            email="reader@pulsenews.local", role=User.Role.READER,
        ),
    )
    users["reader"].set_password("Reader2026!")
    users["reader"].save()
    print(f"Создано/обновлено: {', '.join(users.keys())}\n")

    print("─── Категории ───")
    categories = {}
    for name, desc in [
        ("Политика", "Внутренняя и внешняя политика"),
        ("Технологии", "IT, гаджеты, наука"),
        ("Спорт", "Спортивные события и результаты"),
        ("Культура", "Искусство, кино, музыка"),
    ]:
        cat, _ = Category.objects.get_or_create(name=name, defaults={"description": desc})
        categories[name] = cat
        print(" +", name)
    print()

    print("─── Теги ───")
    tags = {}
    for name in ["Выборы", "IT", "Футбол", "Выставка", "Кино", "Нейросети", "Олимпиада", "Театр"]:
        tag, _ = Tag.objects.get_or_create(name=name)
        tags[name] = tag
        print(" +", name)
    print()

    print("─── Статьи ───")
    now = timezone.now()

    articles_data = [
        # (title, category, author, status, days_ago, summary, body, tags, featured)
        (
            "Правительство объявило о новых мерах поддержки IT-отрасли",
            "Политика", "admin", Article.Status.PUBLISHED, 1,
            "Пакет льгот затронет разработчиков, стартапы и образовательные программы.",
            "Подробности инициативы были озвучены на заседании кабинета министров...",
            ["IT", "Выборы"], True,
        ),
        (
            "Открытие нового технопарка в регионе",
            "Технологии", "editor", Article.Status.PUBLISHED, 2,
            "Площадка объединит 40 резидентов и лаборатории ведущих вузов.",
            "Технопарк рассчитан на 1500 рабочих мест...",
            ["IT", "Нейросети"], False,
        ),
        (
            "Сборная вышла в финал чемпионата",
            "Спорт", "author", Article.Status.PUBLISHED, 3,
            "Решающий матч завершился со счётом 2:1 в пользу нашей команды.",
            "Голы забили на 23-й и 87-й минутах...",
            ["Футбол", "Олимпиада"], True,
        ),
        (
            "Выставка современного искусства открылась в центре города",
            "Культура", "author2", Article.Status.PUBLISHED, 4,
            "Более 80 работ молодых художников представлены до конца месяца.",
            "Экспозиция включает живопись, скульптуру и медиаинсталляции...",
            ["Выставка", "Театр"], False,
        ),
        (
            "Нейросети научились предсказывать погоду точнее синоптиков",
            "Технологии", "author", Article.Status.PUBLISHED, 5,
            "Исследование опубликовано в рецензируемом журнале.",
            "Модель обучена на данных за 50 лет наблюдений...",
            ["Нейросети", "IT"], False,
        ),
        (
            "Премьера нового фильма собрала рекордную кассу",
            "Культура", "author2", Article.Status.PUBLISHED, 7,
            "За первый уикенд — более 500 миллионов рублей.",
            "Режиссёр обещал продолжение...",
            ["Кино"], False,
        ),
        (
            "Черновик: обзор нового гаджета",
            "Технологии", "author", Article.Status.DRAFT, None,
            "Готовится подробный обзор.",
            "Черновик текста, будет дополняться...",
            ["IT"], False,
        ),
        (
            "На проверке: интервью с тренером сборной",
            "Спорт", "author", Article.Status.REVIEW, None,
            "Материал готов, ждёт редактуры.",
            "Полный текст интервью...",
            ["Футбол"], False,
        ),
        (
            "Архив: прошлогодняя выставка",
            "Культура", "author2", Article.Status.ARCHIVED, 300,
            "Материал в архиве.",
            "Событие прошло в прошлом году...",
            ["Выставка"], False,
        ),
        (
            "На проверке: аналитика выборов",
            "Политика", "editor", Article.Status.REVIEW, None,
            "Аналитический материал готовится к публикации.",
            "Разбор результатов по регионам...",
            ["Выборы"], False,
        ),
    ]

    created_articles = []
    for title, cat_name, username, status, days_ago, summary, body, tag_names, featured in articles_data:
        published_at = now - timedelta(days=days_ago) if days_ago is not None else None
        article = Article.objects.create(
            title=title,
            author=users[username],
            category=categories[cat_name],
            summary=summary,
            body=body,
            status=status,
            published_at=published_at,
            is_featured=featured,
            views=random.randint(0, 1500),
        )
        article.tags.set([tags[t] for t in tag_names])
        created_articles.append(article)
        print(f" + [{status}] {title[:50]}...")

    print(f"\nВсего статей: {Article.objects.count()}")
    print(f"Опубликованных (published): {Article.published.count()}\n")

    print("─── Комментарии ───")
    published_articles = [a for a in created_articles if a.status == Article.Status.PUBLISHED]
    comment_texts = [
        "Отличная новость!",
        "Спасибо за подробный разбор.",
        "Не согласен с автором, но интересно.",
        "Когда будет продолжение?",
        "Очень полезно, спасибо редакции.",
        "Ссылка на источник битая.",
        "Согласен с предыдущим комментатором.",
        "Надо бы ещё фото добавить.",
        "Так и знал, что этим кончится.",
        "Поддерживаю инициативу!",
        "А подробности будут?",
        "Хорошая статья, читается легко.",
        "Ждём официальной реакции.",
        "Спасибо, что держите в курсе.",
        "Интересная точка зрения.",
    ]
    commenters = [users["reader"], users["author2"], users["editor"]]

    for i, text in enumerate(comment_texts):
        article = random.choice(published_articles)
        Comment.objects.create(
            article=article,
            author=random.choice(commenters),
            text=text,
            is_approved=(i % 3 != 0),
        )

    print(f"Всего комментариев: {Comment.objects.count()}")
    print(f"Одобрено: {Comment.objects.filter(is_approved=True).count()}")
    print(f"Не одобрено: {Comment.objects.filter(is_approved=False).count()}\n")

    print("✅ Seed завершён.")


if __name__ == "__main__":
    run()