import base64
from typing import Any

from flask import Response, request
from flask_admin import BaseView, expose
from flask_jwt_extended import jwt_required
from flask_wtf.file import FileAllowed, FileField, FileStorage, ValidationError
from sqlalchemy.exc import IntegrityError

from src.admin.base import (
    CustomAdminView,
    IntegrityErrorMixin,
    NotVisibleMixin,
)
from src.constants import (
    CAN_ONLY_BE_ONE_CORRECT_ANSWER,
    DEFAULT_PAGE_NUMBER,
    ERROR_FOR_QUESTION,
    ITEMS_PER_PAGE,
    ONE_ANSWER_VARIANT,
    ONE_CORRECT_ANSWER,
    UNIQUE_VARIANT,
)
from src.crud.question import question_crud
from src.models.question import Question
from src.models.variant import Variant


class QuestionAdmin(IntegrityErrorMixin, CustomAdminView):

    """Добавление и перевод модели вопросов в админ зону."""

    delete_error_message = ERROR_FOR_QUESTION
    # Отображаемые поля в списке записей
    column_list = ['title', 'category', 'is_active']
    # Отображаемые поля в форме создания и редактирования
    form_columns = ['title', 'category', 'is_active']
    column_labels = {
        'id': 'ID',
        'title': 'Текст вопроса',
        'category': 'Категория',
        'is_active': 'Активен',
    }
    form_extra_fields = {
        'image': FileField(
            'Загрузите изображение',
            validators=[
                FileAllowed(
                    ['png', 'jpg', 'jpeg', 'gif'],
                    'Только изображения',
                ),
            ],
        ),
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
        if 'image' in form.data:
            image = form.data['image']
            if image and isinstance(image, FileStorage):
                image_data = image.read()
                model.image = base64.b64encode(image_data).decode('utf-8')
            else:
                model.image = None
        else:
            model.image = None
        try:
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


class QuestionListView(BaseView):

    """Создание списка для статистики."""

    @expose('/')
    @jwt_required()
    def index(self) -> Response:
        """Создание списка для статистики."""
        page = request.args.get('page', DEFAULT_PAGE_NUMBER, type=int)
        per_page = ITEMS_PER_PAGE

        search_query = request.args.get('search', '', type=str)
        query = Question.query
        if search_query:
            query = query.filter(Question.title.ilike(f'%{search_query}%'))

        # Пагинация
        questions = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )

        question_data = [
            {
                'id': question.id,
                'title': question.title,
            }
            for question in questions.items
        ]

        # Передаем данные в шаблон
        return self.render(
            'admin/question_list.html',
            data=question_data,
            pagination=questions,
            search_query=search_query,
        )


class QuestionStatisticsView(NotVisibleMixin):

    """Представление для статистики конкретного вопроса."""

    # Статистика по конкретному вопросу
    @expose('/')
    @jwt_required()
    async def index(self) -> Response:
        """Выполняем запрос статистики для конкретного вопроса."""
        question_id = request.args.get('question_id')

        statictic = await question_crud.get_statistic(question_id)

        (
            question_text,
            total_answers,
            correct_answers,
            correct_percentage,
        ) = statictic

        return self.render(
            'admin/question_statistics.html',
            question_text=question_text,
            total_answers=total_answers,
            correct_answers=correct_answers,
            correct_percentage=correct_percentage,
        )
