from typing import Optional

from sqlalchemy import select

from src import db
from src.crud.base import CRUDBase
from src.models import QuizResult


class CRUDQuizResult(CRUDBase):

    """Круд класс для результатов квиза."""

    def get_by_user_and_quiz(
        self,
        user_id: int,
        quiz_id: int,
    ) -> Optional[QuizResult]:
        """Получить результат квиза с пользователем и квизом."""
        return (
            db.session.execute(
                select(QuizResult).where(
                    QuizResult.user_id == user_id,
                    QuizResult.quiz_id == quiz_id,
                ),
            )
            .scalars()
            .first()
        )


quiz_result_crud = CRUDQuizResult(QuizResult)
