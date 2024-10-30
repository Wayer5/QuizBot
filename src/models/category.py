from src import db
from src.models.base import BaseModel, IsActiveMixin


class Category(BaseModel, IsActiveMixin):

    """Модель рубрики викторины.

    Хранит информацию о различных рубриках викторин.

    """

    __tablename__ = 'categories'

    name = db.Column(
        db.String(30),
        nullable=False,
        unique=True,
        comment='Название рубрики викторины.',
    )

    # # Связь с таблицей quizzes
    # quizzes = db.relationship(
    #     'Quiz',
    #     back_populates='category',
    #     cascade='all,delete',
    #     lazy=True,
    # )

    questions = db.relationship(
        'Question',
        back_populates='category',
        cascade='all,delete',
        lazy=True,
    )

    def __str__(self) -> str:
        """Отображение названия объекта в админ зоне."""
        return self.name
