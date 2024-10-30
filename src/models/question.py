from sqlalchemy.orm import deferred

from src import db
from src.models.base import BaseModel, IsActiveMixin
from src.models.quiz_question import quiz_questions


class Question(BaseModel, IsActiveMixin):

    """Модель вопроса.

    Содержит информацию о вопросах, относящихся к викторине.

    """

    __tablename__ = 'questions'

    title = db.Column(
        db.String(220),
        nullable=False,
        comment='Текст вопроса.',
        unique=True,
    )
    # quiz_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('quizzes.id'),
    #     nullable=True,
    #     comment='Идентификатор викторины, к которой относится вопрос.',
    #     index=True,
    # )
    category_id = db.Column(
        db.Integer,
        db.ForeignKey('categories.id'),
        nullable=False,
        comment='Идентификатор рубрики, к которой относится вопрос.',
        index=True,
    )
    image = deferred(
        db.Column(
            db.Text,
            nullable=True,
            comment='Изображение',
        ),
    )
    # quiz = db.relationship(
    #     'Quiz',
    #     back_populates='questions',
    # )
    quizzes = db.relationship(
        'Quiz',
        secondary=quiz_questions,
        back_populates='questions',
    )
    category = db.relationship(
        'Category',
        back_populates='questions',
    )
    # Связь с таблицей variants
    variants = db.relationship(
        'Variant',
        backref='variants',
        lazy=True,
        cascade='all,delete',
    )

    def __str__(self) -> str:
        """Отображение названия объекта в админ зоне."""
        return f'{self.category.name} - {self.title}'
