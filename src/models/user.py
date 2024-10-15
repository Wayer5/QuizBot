from datetime import datetime

from src import db
from src.models.base import BaseModel, IsActiveMixin, TimestampMixin


class User(BaseModel, TimestampMixin, IsActiveMixin):

    """Модель пользователя.

    Хранит информацию о пользователях.

    """

    __tablename__ = 'users'
    name = db.Column(db.String)
    username = db.Column(db.String, unique=True)
    telegram_id = db.Column(db.BigInteger)
    updated_on = db.Column(
        db.DateTime(),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    is_admin = db.Column(db.Boolean(), default=False)

    # Связь с таблицей QuizResult
    quizzes_results = db.relationship(
        'QuizResult',
        backref='result',
        cascade='all,delete',
        lazy=True,
    )
