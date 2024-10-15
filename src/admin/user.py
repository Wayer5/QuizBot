from flask import Response, request
from flask_admin import BaseView, expose
from flask_jwt_extended import jwt_required

from src.admin.base import CustomAdminView, NotVisibleMixin
from src.constants import (
    DEFAULT_PAGE_NUMBER,
    HTTP_NOT_FOUND,
    ITEMS_PER_PAGE,
    USER_NOT_FOUND_MESSAGE,
)
from src.crud.quiz_result import quiz_result_crud
from src.crud.user_answer import user_answer_crud
from src.models.user import User


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
        'name': 'Имя',
        'username': 'Имя пользователя',
        'telegram_id': 'ID Telegram',
        'created_on': 'Дата создания',
        'updated_on': 'Дата обновления',
        'is_active': 'Активен',
        'is_admin': 'Администратор',
    }


class UserListView(BaseView):

    """Представление для статистики всех пользователей."""

    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Создание списка для статистики пользователей."""
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


class UserStatisticsView(NotVisibleMixin):

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
