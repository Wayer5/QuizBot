from typing import Optional

from sqlalchemy import null, select, true

from src import db
from src.crud.base import CRUDBase
from src.models import Question, UserAnswer


class CRUDQuestion(CRUDBase):

    """Круд класс для вопросов."""

    def get_new(
        self,
        user_id: int,
        quiz_id: int,
        is_active: bool = true(),
    ) -> Optional[Question]:
        """Получить новый вопрос."""
        return (
            db.session.execute(
                select(Question)
                .where(
                    Question.quiz_id == quiz_id,
                    Question.is_active == is_active,
                    UserAnswer.id == null(),
                )
                .outerjoin(
                    UserAnswer,
                    (Question.id == UserAnswer.question_id)
                    & (UserAnswer.user_id == user_id),
                )
                .limit(1),
            )
            .scalars()
            .first()
        )

    def get_all_by_quiz_id(
        self,
        quiz_id: int,
        is_active: bool = true(),
    ) -> list[Question]:
        """Получить все вопросы по идентификатору теста."""
        return (
            db.session.execute(
                select(Question)
                .where(
                    Question.quiz_id == quiz_id,
                    Question.is_active == is_active,
                )
                .order_by(Question.id),
            )
            .scalars()
            .all()
        )


question_crud = CRUDQuestion(Question)
