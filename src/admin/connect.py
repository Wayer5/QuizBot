from flask import request
from flask_admin import Admin
from flask_babel import Babel

from src import app, db
from src.admin.category import (
    CategoryAdmin,
    CategoryListView,
    # CategoryStatisticsView,
)
from src.admin.index import MyAdminIndexView
from src.admin.question import (
    QuestionAdmin,
    QuestionListView,
    QuestionStatisticsView,
)
from src.admin.quiz import QuizAdmin, QuizListView, QuizStatisticsView
from src.admin.user import UserAdmin, UserListView, UserStatisticsView
from src.models.category import Category
from src.models.question import Question
from src.models.quiz import Quiz
from src.models.user import User

# Создания экземпляра админ панели
admin = Admin(
    app,
    name='MedStat_Solutions',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView(),
)


# Добавляем представления в админку
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))
admin.add_view(
    CategoryAdmin(
        Category,
        db.session,
        name='Категории',
        endpoint='category_admin',
    ),
)
admin.add_view(
    QuizAdmin(Quiz, db.session, name='Викторины', endpoint='quiz_admin'),
)
admin.add_view(QuestionAdmin(Question, db.session, name='Вопросы'))

# Добавляем представления для страниц статистик в админку
admin.add_view(
    UserListView(name='Статистика пользователей', endpoint='user_list'),
)
admin.add_view(
    UserStatisticsView(endpoint='user_statistics'),
)
admin.add_view(
    CategoryListView(
        name='Статистика по категориям',
        endpoint='category_list',
    ),
)
# admin.add_view(
#     CategoryStatisticsView(endpoint='category_statistics'),
# )
admin.add_view(
    QuizListView(name='Статистика по викторинам', endpoint='quiz_list'),
)
admin.add_view(
    QuizStatisticsView(endpoint='quiz_statistics'),
)
admin.add_view(
    QuestionListView(name='Статистика по вопросам', endpoint='question_list'),
)
admin.add_view(
    QuestionStatisticsView(
        name='Статистика вопросов',
        endpoint='question_statistics',
    ),
)


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
