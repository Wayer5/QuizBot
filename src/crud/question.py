from typing import Optional, Tuple

from sqlalchemy import null, select, true
from sqlalchemy.exc import DataError
from sqlalchemy.sql import text

from src import db
from src.crud.base import CRUDBase
from src.models.question import Question
from src.models.user_answer import UserAnswer


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

    def get_statistic(self, question_id: int) -> Tuple:
        """Получить статистику по вопросу."""
        try:
            stats_query = text(
                """
                SELECT
                    qu.title AS question_text,
                    COUNT(ua.id) AS total_answers,
                    SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END),
                    ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) *
                    100.0 / COUNT(ua.id), 2)
                FROM questions qu
                LEFT JOIN user_answers ua ON ua.question_id = qu.id
                WHERE qu.id = :question_id
                GROUP BY qu.title
                """,
            )

            statistic = db.session.execute(
                    stats_query, {'question_id': question_id},
            ).fetchone()
        except DataError:
            # Обрабатываем деление на ноль или другие ошибки данных
            db.session.rollback()  # Откатываем сессию
            statistic = ('Нет данных', 0, 0, 0)

        return statistic


question_crud = CRUDQuestion(Question)
