from flask import abort
from sqlalchemy import select, true

from src import db
from src.constants import HTTP_NOT_FOUND
from src.crud.base import CRUDBase
from src.models import Quiz


class CRUDQuiz(CRUDBase):

    """Круд класс викторин."""

    def get_by_category_id(
        self,
        category_id: int,
        is_active: bool = true(),
    ) -> list[Quiz]:
        """Получение викторин по id категории."""
        quizzes = db.session.execute(
            select(Quiz).where(
                Quiz.category_id == category_id,
                Quiz.is_active == is_active,
            ),
        ).scalars().all()
        if not quizzes:
            abort(HTTP_NOT_FOUND)
        return quizzes


quiz_crud = CRUDQuiz(Quiz)
