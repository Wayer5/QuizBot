from src import db
from src.models.base import BaseModel, IsActiveMixin


class Question(BaseModel, IsActiveMixin):

    """Модель вопроса.

    Содержит информацию о вопросах, относящихся к викторине.

    """

    __tablename__ = 'questions'
    title = db.Column(
        db.String(175),
        nullable=False,
        comment='Текст вопроса.',
        unique=True,
    )
    quiz_id = db.Column(
        db.Integer,
        db.ForeignKey('quizzes.id'),
        nullable=False,
        comment='Идентификатор викторины, к которой относится вопрос.',
        index=True,
    )
    quiz = db.relationship(
        'Quiz',
        back_populates='questions',
    )

    # Связь с таблицей variants
    variants = db.relationship(
        'Variant',
        backref='variants',
        lazy=True,
        cascade='all,delete',
    )
