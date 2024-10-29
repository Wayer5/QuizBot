from sqlalchemy import UniqueConstraint

from src import db
from src.models.base import BaseModel


class UserAnswer(BaseModel):

    """Модель ответов пользователей на вопросы.

    Хранит информацию о каждом ответе пользователя на вопросы викторины.

    """

    __tablename__ = 'user_answers'

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True,
        comment='Идентификатор пользователя.',
        index=True,
    )
    tg_user_id = db.Column(
        db.Integer,
        db.ForeignKey('telegram_users.id'),
        nullable=True,
        comment='Идентификатор телеграм пользователя.',
        index=True,
    )
    question_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id'),
        nullable=False,
        comment='Идентификатор вопроса, на который ответил пользователь.',
        index=True,
    )
    answer_id = db.Column(
        db.Integer,
        db.ForeignKey('variants.id'),
        nullable=False,
        comment='Идентификатор выбранного варианта ответа.',
    )
    is_right = db.Column(
        db.Boolean,
        default=False,
        comment='Флаг, указывающий, является ли ответ правильным.',
    )
    __table_args__ = (
        UniqueConstraint(
            'user_id',
            'question_id',
            name='_person_question_uc',
        ),
    )
