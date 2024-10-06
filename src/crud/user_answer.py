from typing import Optional

from sqlalchemy import select

from src import db
from src.crud.base import CRUDBase
from src.models import UserAnswer


class CRUDUserAnswer(CRUDBase):

    """Круд класс для ответов."""
    def get_results_by_user(
        self,
        user_id: int,
    ) -> Optional[UserAnswer]:
        """Получить результаты квизов пользователя."""
        return (
            db.session.execute(
                select(UserAnswer).where(
                    UserAnswer.user_id == user_id,
                ),
            )
            .scalars()
            .all()
        )


user_answer_crud = CRUDUserAnswer(UserAnswer)
