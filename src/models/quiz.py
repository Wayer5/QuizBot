from src import db
from src.models.base import BaseModel, IsActiveMixin


class Quiz(BaseModel, IsActiveMixin):

    """Модель викторины.

    Содержит основную информацию о викторине, такую как название и категория.

    """

    __tablename__ = 'quizzes'

    title = db.Column(
        db.String(30),
        nullable=False,
        comment='Название викторины.',
        unique=True,
    )
    # category_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey('categories.id'),
    #     nullable=False,
    #     comment='Идентификатор категории, к которой относится викторина.',
    # )
    # category = db.relationship('Category', back_populates='quizzes')

    # Связь с таблицей questions
    questions = db.relationship(
        'Question',
        back_populates='quiz',
        lazy=True,
        cascade='all,delete',
    )

    # Связь с таблицей результатов викторины
    results = db.relationship(
        'QuizResult',
        backref='quiz',
    )

    def __str__(self) -> str:
        """Отображение названия объекта в админ зоне."""
        return self.title
