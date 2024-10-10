from typing import Optional

from sqlalchemy import select, true
from sqlalchemy.orm import Query

from src import db
from src.crud.base import CRUDBase
from src.models import Quiz


class CRUDQuiz(CRUDBase):

    """Круд класс викторин."""

    def get_by_category_id(self, category_id: int, is_active: bool = true(),
                           ) -> Query:
        """Получение викторин по id категории как запрос Query."""
        return db.session.query(Quiz).filter(
            Quiz.category_id == category_id, Quiz.is_active == is_active,
        )

    def get_by_id(self, quiz_id: int) -> Optional[Quiz]:
        """Получить викторину по ID."""
        return (
            db.session.execute(
                select(Quiz).where(Quiz.id == quiz_id),
            )
            .scalars()
            .first()
        )


quiz_crud = CRUDQuiz(Quiz)
