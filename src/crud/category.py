from typing import Tuple

from sqlalchemy import true
from sqlalchemy.exc import DataError
from sqlalchemy.orm import Query
from sqlalchemy.sql import text

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

    def get_statistic(self, category_id: int) -> Tuple:
        """Получить статистику по категории."""
        try:
            stats_query = text(
                """
                SELECT
                    c.name AS category_name,
                    COUNT(ua.id) AS total_answers,
                    SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END),
                    ROUND(SUM(CASE WHEN ua.is_right = TRUE THEN 1 ELSE 0 END) *
                    100.0 / COUNT(ua.id), 2)
                FROM categories c
                LEFT JOIN quizzes q ON q.category_id = c.id
                LEFT JOIN questions qu ON qu.quiz_id = q.id
                LEFT JOIN user_answers ua ON ua.question_id = qu.id
                WHERE c.id = :category_id
                GROUP BY c.name
                """,
            )

            statistic = db.session.execute(
                stats_query,
                {'category_id': category_id},
            ).fetchone()
        except DataError:
            # Обрабатываем деление на ноль или другие ошибки данных
            db.session.rollback()  # Откатываем сессию
            statistic = ('Нет данных', 0, 0, 0)

        return statistic


category_crud = CRUDCategory(Category)
