from typing import List, Optional

from sqlalchemy import select

from src import db
from src.crud.base import CRUDBase
from src.models.question import Question
from src.models.user_answer import UserAnswer


class CRUDUserAnswer(CRUDBase):

    """Круд класс для ответов."""

    async def get_results_by_user(
        self, user_id: int, tg_user: bool = False,
    ) -> List[UserAnswer]:
        """Получить результаты квизов пользователя."""
        args = (
            UserAnswer.user_id == user_id
            if not tg_user
            else UserAnswer.tg_user_id == user_id
        )
        return (
            db.session.execute(
                select(UserAnswer).where(args),
            )
            .scalars()
            .all()
        )

    async def get_results_by_user_and_quiz(
        self,
        user_id: int,
        quiz_id: int,
    ) -> Optional[UserAnswer]:
        """Получить результаты ответов пользователя по конкретной викторине."""
        return (
            db.session.execute(
                select(UserAnswer).where(
                    UserAnswer.user_id == user_id,
                    UserAnswer.question_id.in_(
                        select(Question.id).where(Question.quiz_id == quiz_id),
                    ),
                ),
            )
            .scalars()
            .all()
        )


user_answer_crud = CRUDUserAnswer(UserAnswer)
