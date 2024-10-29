from typing import Optional

from sqlalchemy import Result, select
from sqlalchemy.orm import joinedload

from src import db
from src.crud.base import CRUDBase
from src.models.quiz_result import QuizResult


class CRUDQuizResult(CRUDBase):

    """Круд класс для результатов квиза."""

    async def get_by_user_and_quiz(
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

    async def get_results_by_user(
        self,
        user_id: int,
        tg_user: bool = False,
    ) -> Optional[QuizResult]:
        """Получить результаты квизов пользователя."""
        return (
            db.session.execute(
                select(QuizResult)
                # загрузка связанных Quiz
                .options(joinedload(QuizResult.quiz)).where(
                    QuizResult.user_id == user_id
                    if not tg_user
                    else QuizResult.tg_user_id == user_id,
                ),
            )
            .scalars()
            .all()
        )

    async def get_results_by_user_paginated(
        self,
        user_id: int,
        page: int,
        per_page: int,
        tg_user: bool = False,
    ) -> Result:
        """Получить результаты квизов пользователя c пагинацией."""
        if not tg_user:
            query = self.model.query.filter_by(user_id=user_id)
        else:
            query = self.model.query.filter_by(tg_user_id=user_id)

        return query.paginate(
            page=page,
            per_page=per_page,
            error_out=False,
        )


quiz_result_crud = CRUDQuizResult(QuizResult)
