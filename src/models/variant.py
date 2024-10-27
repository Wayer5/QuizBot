from sqlalchemy import UniqueConstraint

from src import db
from src.models.base import BaseModel


class Variant(BaseModel):

    """Модель варианта ответа.

    Содержит информацию о вариантах ответа на вопрос.

    """

    __tablename__ = 'variants'

    question_id = db.Column(
        db.Integer,
        db.ForeignKey('questions.id'),
        nullable=False,
        comment='Идентификатор вопроса, к которому относится данный ответ.',
    )
    title = db.Column(
        db.String(60),
        nullable=False,
        comment='Текст варианта ответа.',
    )
    description = db.Column(
        db.String(650),
        nullable=True,
        comment='Дополнительное описание или пояснение для варианта ответа.',
    )
    is_right_choice = db.Column(
        db.Boolean,
        default=False,
        comment='Флаг, указывающий, является ли данный ответ правильным.',
    )
    __table_args__ = (
        UniqueConstraint(
            'question_id',
            'title',
            name='_question_variant_uc',
        ),
    )
