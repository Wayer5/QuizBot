from flask import request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel

from . import app, db
from .models import Category, Question, Quiz, User, Variant

# Создания экземпляра админ панели
admin = Admin(app, name='MedStat_Solutions', template_mode='bootstrap4')


class UserAdmin(ModelView):

    """Добавление и перевод модели пользователя в админ зону."""

    column_labels = {
        'id': 'ИД',
        'name': 'Имя',
        'username': 'Имя пользователя',
        'telegram_id': 'ID Telegram',
        'created_on': 'Дата создания',
        'updated_on': 'Дата обновления',
        'is_active': 'Активен',
        'is_admin': 'Администратор',
    }


class CategoryAdmin(ModelView):

    """Добавление и перевод модели категорий в админ зону."""

    column_labels = {
        'id': 'ID',
        'name': 'Название',
        'is_active': 'Активен',
    }


class QuizAdmin(ModelView):

    """Добавление и перевод модели викторин в админ зону."""

    # Отображаемые поля в списке записей
    column_list = ['id', 'title', 'category', 'is_active']
    # Отображаемые поля в форме создания и редактирования
    form_columns = ['title', 'category']
    column_labels = {
        'id': 'ID',
        'title': 'Название',
        'category': 'Категория',
        'is_active': 'Активен',
    }


class QuestionAdmin(ModelView):

    """Добавление и перевод модели вопросов в админ зону."""

    # Отображаемые поля в списке записей
    column_list = ['id', 'title', 'quiz', 'is_active']
    column_labels = {
        'id': 'ID',
        'title': 'Текст вопроса',
        'quiz': 'Викторина',
        'is_active': 'Активен',
    }
    # Добаление возможности при создании вопроса
    # сразу добавлять варианты ответов
    inline_models = [(Variant, {
        # Отображаемые поля в форме создания и редактирования.
        # Обязательно нужно прописывать поле 'id'.
        # Его не видно в форме, но без него объекты не будут сохраняться
        'form_columns': ['id', 'title', 'description', 'is_right_choice'],
        # Название формы
        'form_label': 'Вариант',
        # Перевод полей формы
        'column_labels': {
                'title': 'Название',
                'description': 'Описание',
                'is_right_choice': 'Правильный выбор',
            },
    })]


# Добавляем представления в админку
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))
admin.add_view(CategoryAdmin(Category, db.session, name='Категории'))
admin.add_view(QuizAdmin(Quiz, db.session, name='Викторины'))
admin.add_view(QuestionAdmin(Question, db.session, name='Вопросы'))


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
