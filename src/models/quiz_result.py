from datetime import datetime

from sqlalchemy import UniqueConstraint

from src import db
from src.models.base import BaseModel, TimestampMixin


class QuizResult(BaseModel, TimestampMixin):

    """Модель результатов викторины.

    Хранит информацию о прохождении пользователем викторины.
    Такие как количество правильных ответов и статус завершения.

    """

    __tablename__ = 'quiz_results'
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True,
        comment='Идентификатор пользователя, прошедшего викторину.',
    )
    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey('quizzes.id'),
        nullable=False,
        comment='Идентификатор викторины.',
    )
    total_questions = db.Column(
        db.Integer,
        nullable=False,
        comment='Общее количество вопросов в викторине.',
    )
    correct_answers_count = db.Column(
        db.Integer,
        nullable=False,
        comment='Количество правильных ответов, данных пользователем.',
    )
    is_complete = db.Column(
        db.Boolean,
        default=False,
        comment='Флаг завершения викторины.',
    )

    ended_on = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'quiz_id',
            name='_person_quiz_uc',
        ),
    )
