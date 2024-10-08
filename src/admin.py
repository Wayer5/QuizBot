from typing import Any

from flask import request
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel

from . import app, db
from .models import Category, Question, Quiz, User, Variant

# Создания экземпляра админ панели
admin = Admin(app, name='MedStat_Solutions', template_mode='bootstrap4')


class CustomAdminView(ModelView):

    """Добавление в формы с CSRF."""

    list_template = 'csrf/list.html'
    edit_template = 'csrf/edit.html'
    create_template = 'csrf/create.html'


class UserAdmin(CustomAdminView):

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


class CategoryAdmin(CustomAdminView):

    """Добавление и перевод модели категорий в админ зону."""

    column_labels = {
        'id': 'ID',
        'name': 'Название',
        'is_active': 'Активен',
    }


class QuizAdmin(CustomAdminView):

    """Добавление и перевод модели викторин в админ зону."""

    # Отображаемые поля в списке записей
    column_list = ['id', 'title', 'category', 'is_active']
    # Отображаемые поля в форме создания и редактирования
    form_columns = ['title', 'category', 'is_active']

    column_labels = {
        'id': 'ID',
        'title': 'Название',
        'category': 'Категория',
        'is_active': 'Активен',
    }


class QuestionAdmin(CustomAdminView):

    """Добавление и перевод модели вопросов в админ зону."""

    # Отображаемые поля в списке записей
    column_list = ['id', 'title', 'quiz', 'is_active']
    column_labels = {
        'id': 'ID',
        'title': 'Текст вопроса',
        'quiz': 'Викторина',
        'is_active': 'Активен',
    }

    # Добаление возможности при создании вопроса сразу добавлять
    # варианты ответов
    inline_models = [
        (
            Variant,
            {
                # Отображаемые поля в форме создания и редактирования.
                # Обязательно нужно прописывать поле 'id'.
                # Его не видно в форме,
                # но без него объекты не будут сохраняться
                'form_columns': [
                    'id',
                    'title',
                    'description',
                    'is_right_choice',
                ],
                # Название формы
                'form_label': 'Вариант',
                # Перевод полей формы
                'column_labels': {
                    'title': 'Название',
                    'description': 'Описание',
                    'is_right_choice': 'Правильный выбор',
                },
            },
        ),
    ]

    def on_model_change(self, form: Any, model: Any, is_created: bool) -> None:
        """Проверка на количество правильных вариантов."""
        # Получаем все варианты для вопроса
        variants = form.variants.entries

        # Проверка на наличие хотя бы одного варианта ответа
        if not variants:
            raise ValueError("Должен быть хотя бы один вариант ответа.")

        # Получаем список правильных вариантов
        correct_answers = [v for v in variants if v.is_right_choice.data]

        # Проверка, что правильный вариант только один
        if len(correct_answers) > 1:
            raise ValueError("Может быть только один правильный ответ.")

        # Проверка, что есть хотя бы один правильный вариант
        if len(correct_answers) == 0:
            raise ValueError("Должен быть хотя бы один правильный ответ.")

        # Вызов родительского метода для сохранения изменений
        super(QuestionAdmin, self).on_model_change(form, model, is_created)


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
