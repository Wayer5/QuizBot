from typing import Any

from flask import Response, request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from wtforms import ValidationError

from . import app, db
from .constants import (
    CAN_ONLY_BE_ONE_CORRECT_ANSWER,
    ONE_ANSWER_VARIANT,
    ONE_CORRECT_ANSWER,
    UNIQUE_VARIANT,
)
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
    # Добаление возможности при создании вопроса
    # сразу добавлять варианты ответов
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
        """Проверка на количество правильных вариантов и обработка ошибок."""
        try:
            # Попытка сохранения модели
            super(QuestionAdmin, self).on_model_change(form, model, is_created)

            # Обрабатываем инлайн модели (Variants)
            for variant in model.variants:
                if self.is_duplicate_variant(variant):
                    raise ValidationError(UNIQUE_VARIANT)

        except IntegrityError as e:
            # Проверяем ошибку уникальности
            error_message = ('duplicate key value violates unique '
                             'constraint "_question_variant_uc"')
            if error_message in str(e.orig):
                raise ValidationError(UNIQUE_VARIANT)
            # Если другая ошибка — выбрасываем её заново
            raise e

        # Получаем все варианты для вопроса
        variants = form.variants.entries

        # Проверка на наличие хотя бы одного варианта ответа
        if not variants:
            raise ValueError(ONE_ANSWER_VARIANT)

        # Получаем список правильных вариантов
        correct_answers = [v for v in variants if v.is_right_choice.data]

        # Проверка, что правильный вариант только один
        if len(correct_answers) > 1:
            raise ValueError(CAN_ONLY_BE_ONE_CORRECT_ANSWER)

        # Проверка, что есть хотя бы один правильный вариант
        if len(correct_answers) == 0:
            raise ValueError(ONE_CORRECT_ANSWER)

        # Вызов родительского метода для сохранения изменений
        super(QuestionAdmin, self).on_model_change(form, model, is_created)

    def is_duplicate_variant(self, variant: Variant) -> bool:
        """Проверка на дублирующиеся варианты по полям question_id и title.

        Args:
        ----
        self: Экземпляр класса.
        variant: Объект модели Variant.

        Returns:
        -------
        bool

        """
        # Получаем все записи с таким же question_id и title
        existing_variant = Variant.query.filter_by(
            question_id=variant.question_id, title=variant.title,
        ).first()
        # Проверяем, существует ли такая запись, и это не текущий объект
        if existing_variant and existing_variant.id != variant.id:
            return True
        return False


class QuestionListView(BaseView):

    """Создание списка для статистики."""

    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Количество вопросов на странице
        offset = (page - 1) * per_page

        # Запрос для получения списка вопросов с учетом пагинации
        query = text(
            'SELECT id, title FROM questions LIMIT :limit OFFSET :offset',
        )
        questions = db.session.execute(
            query, {'limit': per_page, 'offset': offset},
        ).fetchall()

        # Запрос для получения общего количества вопросов
        count_query = text('SELECT COUNT(id) FROM questions')
        total_questions = db.session.execute(count_query).scalar()

        # Общее количество страниц
        total_pages = (total_questions + per_page - 1) // per_page

        # Передаем данные в шаблон
        return self.render('admin/question_list.html',
                           questions=questions,
                           page=page,
                           total_pages=total_pages)


class QuizListView(BaseView):

    """Создание списка для статистики."""

    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Количество викторин на странице
        offset = (page - 1) * per_page

        # Запрос для получения списка викторин с учетом пагинации
        query = text(
            'SELECT id, title FROM quizzes LIMIT :limit OFFSET :offset',
        )
        quizzes = db.session.execute(
            query, {'limit': per_page, 'offset': offset},
        ).fetchall()

        # Запрос для получения общего количества викторин
        count_query = text('SELECT COUNT(id) FROM quizzes')
        total_quizzes = db.session.execute(count_query).scalar()

        # Общее количество страниц
        total_pages = (total_quizzes + per_page - 1) // per_page

        # Передаем данные в шаблон
        return self.render('admin/quiz_list.html',
                           quizzes=quizzes,
                           page=page,
                           total_pages=total_pages)


class CategoryListView(BaseView):

    """Создание списка для статистики."""

    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Количество категорий на странице
        offset = (page - 1) * per_page

        # Запрос для получения списка категорий с учетом пагинации
        query = text(
            'SELECT id, name FROM categories LIMIT :limit OFFSET :offset',
        )
        categories = db.session.execute(
            query, {'limit': per_page, 'offset': offset},
        ).fetchall()

        # Запрос для получения общего количества категорий
        count_query = text('SELECT COUNT(id) FROM categories')
        total_categories = db.session.execute(count_query).scalar()

        # Общее количество страниц
        total_pages = (total_categories + per_page - 1) // per_page

        # Передаем данные в шаблон
        return self.render('admin/category_list.html',
                           categories=categories,
                           page=page,
                           total_pages=total_pages)


# Добавляем представления в админку
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))
admin.add_view(CategoryAdmin(Category, db.session, name='Категории'))
admin.add_view(QuizAdmin(Quiz, db.session, name='Викторины'))
admin.add_view(QuestionAdmin(Question, db.session, name='Вопросы'))
admin.add_view(QuestionListView(name='Статистика по вопросам'))
admin.add_view(QuizListView(name='Статистика по викторинам'))
admin.add_view(CategoryListView(name='Статистика по категориям'))


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
