from src import db
from src.models.base import BaseModel, TimestampMixin


class TelegramUser(BaseModel, TimestampMixin):

    """Модель для хранения информации о пользователях Telegram."""

    __tablename__ = 'telegram_users'
    telegram_id = db.Column(
        db.BigInteger,
        unique=True,
        nullable=False,
        comment='Уникальный идентификатор пользователя в Telegram.',
        index=True,
    )
    first_name = db.Column(
        db.String(100),
        nullable=False,
        comment='Имя пользователя в Telegram.',
    )
    last_name = db.Column(
        db.String(100),
        nullable=True,
        comment='Фамилия пользователя в Telegram.',
    )
    username = db.Column(
        db.String(100),
        nullable=True,
        unique=True,
        comment='Имя пользователя в Telegram (username).',
    )
    language_code = db.Column(
        db.String(10),
        nullable=True,
        comment='Язык пользователя в формате IETF.',
    )
    is_premium = db.Column(
        db.Boolean,
        default=False,
        comment='Указывает, есть ли у пользователя премиум в Telegram.',
    )
    added_to_attachment_menu = db.Column(
        db.Boolean,
        default=False,
        comment='Указывает, добавил ли пользователь бота в меню вложений.',
    )

    def __repr__(self) -> str:
        return f'<TelegramUser id={self.telegram_id}'
