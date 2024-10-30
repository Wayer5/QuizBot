from typing import Tuple

from sqlalchemy.orm import Query

from src import db
from src.crud.base import CRUDBase
from src.models.category import Category
from src.models.question import Question
from src.models.user_answer import UserAnswer


class CRUDCategory(CRUDBase):

    """Круд класс для рубрик."""

    def get_query(self) -> Query:
        """Получить все активные рубрики как запрос Query."""
        return db.session.query(Category)

    async def get_statistic(self, category_id: int) -> Tuple:
        """Получить статистику по категории."""
        try:
            category = (
                db.session.query(Category.name)
                .filter(Category.id == category_id)
                .first()
            )
            if not category:
                return ('Нет данных', 0, 0, 0)

            category_name = category.name

            # Выбираем все ответы, относящиеся к данной категории.
            results = (
                db.session.query(UserAnswer.is_right)
                .where(
                    UserAnswer.question_id == Question.id,
                    Question.category_id == category_id)
                .all()
            )

            total_answers = len(results)
            correct_answers = sum(1 for result in results if result.is_right)

            if total_answers > 0:
                correct_percentage = round(
                    (correct_answers / total_answers) * 100.0,
                    2,
                )
            else:
                correct_percentage = 0

            return (
                category_name,
                total_answers,
                correct_answers,
                correct_percentage,
            )
        except Exception:
            db.session.rollback()
            return ('Нет данных', 0, 0, 0)


category_crud = CRUDCategory(Category)
