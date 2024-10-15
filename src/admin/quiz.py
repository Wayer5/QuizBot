from flask import Response, redirect, request, url_for
from flask_admin import BaseView, expose
from flask_admin.model.template import LinkRowAction
from flask_jwt_extended import jwt_required

from src.admin.base import (
    CustomAdminView,
    IntegrityErrorMixin,
    NotVisibleMixin,
)
from src.constants import (
    DEFAULT_PAGE_NUMBER,
    ERROR_FOR_QUIZ,
    ITEMS_PER_PAGE,
)
from src.crud.quiz import quiz_crud
from src.models.quiz import Quiz


class QuizAdmin(IntegrityErrorMixin, CustomAdminView):

    """Добавление и перевод модели викторин в админ зону."""

    delete_error_message = ERROR_FOR_QUIZ
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
                'questions',
                category_id=quiz.category_id,
                quiz_id=quiz_id,
                test=True,
            ),
        )


class QuizListView(BaseView):

    """Создание списка викторин для статистики."""

    @expose('/')
    def index(self) -> Response:
        """Создание списка для статистики викторин."""
        page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
        per_page = ITEMS_PER_PAGE

        search_query = request.args.get('search', '', type=str)
        query = Quiz.query
        if search_query:
            query = query.filter(Quiz.title.ilike(f'%{search_query}%'))

        # Пагинация
        quizzes = query.paginate(page=page, per_page=per_page, error_out=False)

        quiz_data = [
            {
                'id': quiz.id,
                'title': quiz.title,
            }
            for quiz in quizzes.items
        ]

        # Передаем данные в шаблон
        return self.render('admin/quiz_list.html',
                           data=quiz_data,
                           pagination=quizzes,
                           search_query=search_query)


class QuizStatisticsView(NotVisibleMixin):

    """Представление для статистики конкретной викторины."""

    # Статистика по конкретному вопросу
    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Выполняем запрос статистики для конкретной викторины."""
        quiz_id = request.args.get('quiz_id')

        statictic = quiz_crud.get_statistic(quiz_id)

        (
            quiz_title, total_answers,
            correct_answers, correct_percentage,
        ) = statictic

        return self.render('admin/quiz_statistics.html', quiz_title=quiz_title,
                           total_answers=total_answers,
                           correct_answers=correct_answers,
                           correct_percentage=correct_percentage)
