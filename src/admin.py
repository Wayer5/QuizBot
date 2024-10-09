from http import HTTPStatus
from typing import Any

from flask import Response, render_template, request
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_babel import Babel

from . import app, db
from .constants import (
    CAN_ONLY_BE_ONE_CORRECT_ANSWER,
    ONE_ANSWER_VARIANT,
    ONE_CORRECT_ANSWER,
    USER_NOT_FOUND_MESSAGE,
)
from .crud.quiz_result import quiz_result_crud
from .crud.user_answer import user_answer_crud
from .models import (
    Category,
    Question,
    Quiz,
    User,
    Variant,
)

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


class UserActivityView(BaseView):

    """Добавление и перевод модели викторин в админ зону."""

    @expose('/')
    def index(self) -> Response:
        """Получение текущей страницы из запроса."""
        page = request.args.get('page', 1, type=int)
        per_page = 5

        # Получение данных о пользователях из базы данных с пагинацией
        users = User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        user_data = [{
            'id': user.id,
            'name': user.name,
            'telegram_id': user.telegram_id,
            'created_on': user.created_on,
            } for user in users.items]

        return self.render(
            'admin/user_activity.html', data=user_data, pagination=users,
            )


@app.route('/user_statistics')
def user_statistics() -> Response:
    """Статистика пользователя."""
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return USER_NOT_FOUND_MESSAGE, HTTPStatus.NOT_FOUND
    quiz_results = quiz_result_crud.get_results_by_user(user_id=user.id)
    user_answers = user_answer_crud.get_results_by_user(user_id=user.id)
    total_questions_answered = len(user_answers)
    total_correct_answers = sum(
        1 for answer in user_answers if answer.is_right
    )
    correct_percentage = (
        total_correct_answers / total_questions_answered * 100
    ) if total_questions_answered > 0 else 0

    return render_template(
        'admin/user_statistics.html',
        user=user,
        total_questions_answered=total_questions_answered,
        total_correct_answers=total_correct_answers,
        correct_percentage=round(correct_percentage),
        quiz_results=quiz_results,
    )


# Добавляем представления в админку
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))
admin.add_view(CategoryAdmin(Category, db.session, name='Категории'))
admin.add_view(QuizAdmin(Quiz, db.session, name='Викторины'))
admin.add_view(QuestionAdmin(Question, db.session, name='Вопросы'))
admin.add_view(UserActivityView(
    name='Статистика активности пользователей', endpoint='user_activity',
))


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
