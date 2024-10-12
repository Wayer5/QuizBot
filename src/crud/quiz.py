from typing import Optional, Tuple

from sqlalchemy import select, true
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Query
from sqlalchemy.sql import text

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

    def get_statistic(self, quiz_id: int) -> Tuple:
        """Получить статистику по викторине."""
        try:
            stats_query = text(
                """
                SELECT
                    q.title AS quiz_title,
                    COUNT(ua.id) AS total_answers,
                    SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END),
                    ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) *
                    100.0 / COUNT(ua.id), 2)
                FROM quizzes q
                LEFT JOIN questions qu ON q.id = qu.quiz_id
                LEFT JOIN user_answers ua ON ua.question_id = qu.id
                WHERE q.id = :quiz_id
                GROUP BY q.title
                """,
            )

            statistic = db.session.execute(
                stats_query, {'quiz_id': quiz_id},
            ).fetchone()
        except DataError:
            # Обрабатываем деление на ноль или другие ошибки данных
            db.session.rollback()  # Откатываем сессию
            statistic = ('Нет данных', 0, 0, 0)

        return statistic


quiz_crud = CRUDQuiz(Quiz)
