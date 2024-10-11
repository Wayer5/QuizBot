from typing import Any

from flask import Response, redirect, request, url_for
from flask_admin import Admin, AdminIndexView, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.model.template import LinkRowAction
from flask_babel import Babel
from flask_jwt_extended import (
    current_user,
    jwt_required,
    verify_jwt_in_request,
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text
from wtforms import ValidationError

from . import app, db
from .constants import (
    CAN_ONLY_BE_ONE_CORRECT_ANSWER,
    DEFAULT_PAGE_NUMBER,
    HTTP_NOT_FOUND,
    ITEMS_PER_PAGE,
    ONE_ANSWER_VARIANT,
    ONE_CORRECT_ANSWER,
    UNIQUE_VARIANT,
    USER_NOT_FOUND_MESSAGE,
)
from .crud.quiz import quiz_crud
from .crud.quiz_result import quiz_result_crud
from .crud.user_answer import user_answer_crud
from .models import Category, Question, Quiz, User, Variant

# # Создания экземпляра админ панели
# admin = Admin(app, name='MedStat_Solutions', template_mode='bootstrap4')


class MyAdminIndexView(AdminIndexView):

    """Класс для переопределения главной страницы администратора."""

    @expose('/')
    def index(self) -> Response:
        """Переопределение главной страницы администратора."""
        admin_menu = self.admin.menu()
        return self.render('admin_index.html', admin_menu=admin_menu)


# Создания экземпляра админ панели
admin = Admin(
    app,
    name='MedStat_Solutions',
    template_mode='bootstrap4',
    index_view=MyAdminIndexView(),
)


class CustomAdminView(ModelView):

    """Добавление в формы с CSRF."""

    list_template = 'csrf/list.html'
    edit_template = 'csrf/edit.html'
    create_template = 'csrf/create.html'

    def is_accessible(self) -> bool:
        """Проверка доступа."""
        verify_jwt_in_request()
        return current_user.is_admin


class UserAdmin(CustomAdminView):

    """Добавление и перевод модели пользователя в админ зону."""

    column_list = [
        'username',
        'is_active',
        'is_admin',
        'name',
        'telegram_id',
        'created_on',
        'updated_on',
    ]

    column_labels = {
        # 'id': 'ID',
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
        # 'id': 'ID',
        'name': 'Название',
        'is_active': 'Активен',
    }


class QuizAdmin(CustomAdminView):

    """Добавление и перевод модели викторин в админ зону."""

    # Отображаемые поля в списке записей
    column_list = ['title', 'category', 'is_active']
    # Отображаемые поля в форме создания и редактирования
    form_columns = ['title', 'category', 'is_active']

    column_labels = {
        'id': 'ID',
        'title': 'Название',
        'category': 'Категория',
        'is_active': 'Активен',
    }

    column_extra_row_actions = [
        LinkRowAction(
            'fa fa-play',
            url='test_question/{row_id}/',
            title='Пробное прохождение',
        ),
    ]

    @expose('/test_question/<int:quiz_id>/')
    def test_quiz_view(self, quiz_id: int) -> Response:
        """Перенаправление на страницу тестирования."""
        quiz = quiz_crud.get(quiz_id)
        return redirect(
            url_for(
                'question',
                category_id=quiz.category_id,
                quiz_id=quiz_id,
                test=True,
            ),
        )


class QuestionAdmin(CustomAdminView):

    """Добавление и перевод модели вопросов в админ зону."""

    # Отображаемые поля в списке записей
    column_list = ['title', 'quiz', 'is_active']
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
            error_message = (
                'duplicate key value violates unique '
                'constraint "_question_variant_uc"'
            )
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
            question_id=variant.question_id,
            title=variant.title,
        ).first()
        # Проверяем, существует ли такая запись, и это не текущий объект
        if existing_variant and existing_variant.id != variant.id:
            return True
        return False


class UserActivityView(BaseView):

    """Представление для статистики всех пользователей."""

    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Получение текущей страницы из запроса."""
        page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
        per_page = ITEMS_PER_PAGE
        search_query = request.args.get('search', '', type=str)
        query = User.query
        if search_query:
            query = query.filter(User.name.ilike(f'%{search_query}%'))

        # Пагинация
        users = query.paginate(page=page, per_page=per_page, error_out=False)

        user_data = [
            {
                'id': user.id,
                'name': user.name,
                'telegram_id': user.telegram_id,
                'created_on': user.created_on,
            }
            for user in users.items
        ]

        return self.render(
            'admin/user_list.html',
            data=user_data,
            pagination=users,
            search_query=search_query,
        )


class UserStatisticsView(BaseView):

    """Представление для статистики конкретного пользователя."""

    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Cтатистика конкретного пользователя."""
        user_id = request.args.get('user_id')
        if not user_id:
            return USER_NOT_FOUND_MESSAGE, HTTP_NOT_FOUND
        user = User.query.get(user_id)
        if not user:
            return USER_NOT_FOUND_MESSAGE, HTTP_NOT_FOUND
        quiz_results = quiz_result_crud.get_results_by_user(user_id=user.id)
        user_answers = user_answer_crud.get_results_by_user(user_id=user.id)
        total_questions_answered = len(user_answers)
        total_correct_answers = sum(
            1 for answer in user_answers if answer.is_right
        )
        correct_percentage = (
            (total_correct_answers / total_questions_answered * 100)
            if total_questions_answered > 0
            else 0
        )

        return self.render(
            'admin/user_statistics.html',
            user=user,
            total_questions_answered=total_questions_answered,
            total_correct_answers=total_correct_answers,
            correct_percentage=round(correct_percentage),
            quiz_results=quiz_results,
        )

    def is_visible(self) -> bool:
        """Скрывает представление из основного меню Flask-Admin."""
        return False


class CategoryListView(BaseView):

    """Создание списка для статистики."""

    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Количество категорий на странице
        offset = (page - 1) * per_page

        # Запрос для получения списка категорий с учетом пагинации
        # query = text(
        #     'SELECT id, name FROM categories LIMIT :limit OFFSET :offset',
        # )

        search_query = request.args.get('search', '', type=str)
        query = Category.query
        if search_query:
            query = query.filter(Category.name.ilike(f'%{search_query}%'))

        # Пагинация
        categories = query.paginate(page=page, per_page=per_page, error_out=False)

        # categories = db.session.execute(
        #     query, {'limit': per_page, 'offset': offset},
        # ).fetchall()

        # Запрос для получения общего количества категорий
        count_query = text('SELECT COUNT(id) FROM categories')
        total_categories = db.session.execute(count_query).scalar()

        # Общее количество страниц
        total_pages = (total_categories + per_page - 1) // per_page

        # Передаем данные в шаблон
        return self.render('admin/category_list.html',
                           categories=categories,
                           page=page,
                           total_pages=total_pages,
                           search_query=search_query,)


class CategoryStatisticsView(BaseView):

    """Представление для статистики конкретной категории."""

    # Статистика по конкретной категории
    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Выполняем запрос статистики для конкретной категории."""
        category_id = request.args.get('category_id')

        stats_query = text("""
            SELECT
                c.name AS category_name,
                COUNT(ua.id) AS total_answers,
                SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_ans,
                ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 /
                    COUNT(ua.id), 2) AS correct_percentage
            FROM categories c
            LEFT JOIN quizzes q ON q.category_id = c.id
            LEFT JOIN questions qu ON qu.quiz_id = q.id
            LEFT JOIN user_answers ua ON ua.question_id = qu.id
            WHERE c.id = :category_id
            GROUP BY c.name
        """)

        result = db.session.execute(
            stats_query, {'category_id': category_id},
        ).fetchone()

        if result:
            category_name = result[0]  # Название категории
            total_answers = result[1]
            correct_ans = result[2]
            correct_percentage = result[3]
        else:
            category_name = "Нет данных"
            total_answers = correct_answers = correct_percentage = 0

        correct_answers = correct_ans

        return self.render('admin/category_statistics.html',
                           category_name=category_name,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)

    def is_visible(self) -> bool:
        """Скрывает представление из основного меню Flask-Admin."""
        return False


class QuizListView(BaseView):

    """Создание списка для статистики."""

    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Количество викторин на странице
        offset = (page - 1) * per_page

        search_query = request.args.get('search', '', type=str)
        query = Quiz.query
        if search_query:
            query = query.filter(Quiz.title.ilike(f'%{search_query}%'))

        # Пагинация
        quizzes = query.paginate(page=page, per_page=per_page, error_out=False)

        # # Запрос для получения списка викторин с учетом пагинации
        # query = text(
        #     'SELECT id, title FROM quizzes LIMIT :limit OFFSET :offset',
        # )
        # quizzes = db.session.execute(
        #     query, {'limit': per_page, 'offset': offset},
        # ).fetchall()

        # Запрос для получения общего количества викторин
        count_query = text('SELECT COUNT(id) FROM quizzes')
        total_quizzes = db.session.execute(count_query).scalar()

        # Общее количество страниц
        total_pages = (total_quizzes + per_page - 1) // per_page

        # Передаем данные в шаблон
        return self.render('admin/quiz_list.html',
                           quizzes=quizzes,
                           page=page,
                           total_pages=total_pages,
                           search_query=search_query,)


class QuizStatisticsView(BaseView):

    """Представление для статистики конкретной викторины."""

    # Статистика по конкретному вопросу
    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        quiz_id = request.args.get('quiz_id')
        stats_query = text("""
            SELECT
                q.title AS quiz_title,
                COUNT(ua.id) AS total_answers,
                SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_ans,
                ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 /
                    COUNT(ua.id), 2) AS correct_percentage
            FROM quizzes q
            LEFT JOIN questions qu ON q.id = qu.quiz_id
            LEFT JOIN user_answers ua ON ua.question_id = qu.id
            WHERE q.id = :quiz_id
            GROUP BY q.title
        """)

        result = db.session.execute(
            stats_query, {'quiz_id': quiz_id}
        ).fetchone()

        if result:
            quiz_title = result[0]  # Название викторины
            total_answers = result[1]
            correct_ans = result[2]
            correct_percentage = result[3]
        else:
            quiz_title = "Нет данных"
            total_answers = correct_answers = correct_percentage = 0

        correct_answers = correct_ans

        return self.render('admin/quiz_statistics.html', quiz_title=quiz_title,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)

    def is_visible(self) -> bool:
        """Скрывает представление из основного меню Flask-Admin."""
        return False


class QuestionListView(BaseView):

    """Создание списка для статистики."""

    @jwt_required()
    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', 1, type=int)
        per_page = 5  # Количество вопросов на странице
        offset = (page - 1) * per_page

        search_query = request.args.get('search', '', type=str)
        query = Question.query
        if search_query:
            query = query.filter(Question.title.ilike(f'%{search_query}%'))

        # Пагинация
        questions = query.paginate(page=page, per_page=per_page, error_out=False)

        # # Запрос для получения списка вопросов с учетом пагинации
        # query = text(
        #     'SELECT id, title FROM questions LIMIT :limit OFFSET :offset',
        # )
        # questions = db.session.execute(
        #     query, {'limit': per_page, 'offset': offset},
        # ).fetchall()

        # Запрос для получения общего количества вопросов
        count_query = text('SELECT COUNT(id) FROM questions')
        total_questions = db.session.execute(count_query).scalar()

        # Общее количество страниц
        total_pages = (total_questions + per_page - 1) // per_page

        # Передаем данные в шаблон
        return self.render('admin/question_list.html',
                           questions=questions,
                           page=page,
                           total_pages=total_pages,
                           search_query=search_query,)


class QuestionStatisticsView(BaseView):

    """Представление для статистики конкретного вопроса."""

    # Статистика по конкретному вопросу
    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Выполняем запрос статистики для конкретного вопроса."""
        question_id = request.args.get('question_id')
        stats_query = text("""
            SELECT
                qu.title AS question_text,
                COUNT(ua.id) AS total_answers,
                SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) AS correct_ans,
                ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) * 100.0 /
                    COUNT(ua.id), 2) AS correct_percentage
            FROM questions qu
            LEFT JOIN user_answers ua ON ua.question_id = qu.id
            WHERE qu.id = :question_id
            GROUP BY qu.title
        """)

        result = db.session.execute(
            stats_query, {'question_id': question_id},
        ).fetchone()

        if result:
            question_text = result[0]  # Доступ к вопросу по индексу
            total_answers = result[1]
            correct_ans = result[2]
            correct_percentage = result[3]
        else:
            question_text = "Нет данных"
            total_answers = correct_answers = correct_percentage = 0

        correct_answers = correct_ans

        return self.render('admin/question_statistics.html',
                           question_text=question_text,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)

    def is_visible(self) -> bool:
        """Скрывает представление из основного меню Flask-Admin."""
        return False


# Добавляем представления в админку
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))
admin.add_view(CategoryAdmin(
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
admin.add_view(UserActivityView(
    name='Статистика пользователей',
    endpoint='user_list',)
)
admin.add_view(UserStatisticsView(
    endpoint='user_statistics',)
)
admin.add_view(CategoryListView(
    name='Статистика по категориям',
    endpoint='category_list',)
)
admin.add_view(CategoryStatisticsView(
    endpoint='category_statistics',)
)
admin.add_view(QuizListView(
    name='Статистика по викторинам',
    endpoint='quiz_list',)
)
admin.add_view(QuizStatisticsView(
    endpoint='quiz_statistics',)
)
admin.add_view(QuestionListView(
    name='Статистика по вопросам',
    endpoint='question_list',)
)
admin.add_view(QuestionStatisticsView(
    name='Статистика вопросов',
    endpoint='question_statistics',)
)


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
