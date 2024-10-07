from flask import request, render_template
from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView
from flask_admin.form import SecureForm
from flask_babel import Babel
from sqlalchemy import func

from . import app, db
from .models import (
    Category,
    Question,
    Quiz,
    QuizResult,
    User,
    UserAnswer,
    Variant
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

    form_base_class = SecureForm
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
    form_columns = ['title', 'category']
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


class QuizResultAdmin(CustomAdminView):

    """Добавление и перевод модели результатов викторин в админ зону."""
    form_columns = [
        'id',
        'user_id',
        'quiz_id',
        'correct_answers_count',
        'total_questions',
        'is_complete',
        'question_id',
    ]

    fields = [
        'id',
        'user_id',
        'quiz_id',
        'correct_answers_count',
        'total_questions',
        'is_complete',
        'question_id',
    ]


class UserActivityView(BaseView):

    """Статистика активности пользователей."""

    @expose('/')
    def index(self):
        # Получение текущей страницы из запроса
        page = request.args.get('page', 1, type=int)
        per_page = 5

        # Получение данных о пользователях из базы данных с пагинацией
        users = User.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        user_data = [{
            'id': user.id,
            'name': user.name,
            'telegram_id': user.telegram_id,
            'created_on': user.created_on
            } for user in users.items]

        return self.render(
            'admin/user_activity.html', data=user_data, pagination=users
            )


@app.route('/user_statistics')
def user_statistics():
    user_id = request.args.get('user_id')
    user = User.query.get(user_id)

    if not user:
        return "Пользователь не найден", 404

    # Получение всех результатов викторин пользователя
    quiz_results = QuizResult.query.filter_by(user_id=user.id).all()
    # Вычисление общего количества отвеченных вопросов
    total_questions_answered = db.session.query(func.count(UserAnswer.id)).filter_by(user_id=user.id).scalar()
    # Вычисление общего количества правильных ответов
    total_correct_answers = db.session.query(func.count(UserAnswer.id)).filter_by(user_id=user.id, is_right=True).scalar()

    # Вычисление процентного соотношения правильных ответов
    correct_percentage = (total_correct_answers / total_questions_answered * 100) if total_questions_answered > 0 else 0

    return render_template(
        'admin/user_statistics.html',
        user=user,
        total_questions_answered=total_questions_answered,
        total_correct_answers=total_correct_answers,
        correct_percentage=round(correct_percentage, 2),
        quiz_results=quiz_results
    )


# Добавляем представления в админку
admin.add_view(UserAdmin(User, db.session, name='Пользователи'))
admin.add_view(CategoryAdmin(Category, db.session, name='Категории'))
admin.add_view(QuizAdmin(Quiz, db.session, name='Викторины'))
admin.add_view(QuestionAdmin(Question, db.session, name='Вопросы'))
admin.add_view(UserActivityView(
    name='Статистика активности пользователей', endpoint='user_activity'
))
admin.add_view(QuizResultAdmin(
    QuizResult, db.session, name='Результаты викторин'
))


def get_locale() -> dict:
    """Возвращает язык из аргументов URL или по умолчанию русский."""
    return request.args.get('lang', 'ru')


# Babel - библиотека для перевода интерфейса на другие языки
babel = Babel(app, locale_selector=get_locale)
