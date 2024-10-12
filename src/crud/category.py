from sqlalchemy import true
from sqlalchemy.orm import Query

from src import db
from src.crud.base import CRUDBase
from src.models import Category, Question, Quiz


class CRUDCategory(CRUDBase):

    """Круд класс для рубрик."""

    def get_active(self, is_active: bool = true()) -> Query:
        """Получить все активные рубрики как запрос Query."""
        return db.session.query(Category).filter(
            Category.is_active == is_active,
            Category.quizzes.any(
                Quiz.is_active == is_active,
            ),
            Category.quizzes.any(
                Quiz.questions.any(Question.is_active == is_active),
            ),
        )


category_crud = CRUDCategory(Category)
