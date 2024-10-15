from datetime import datetime

from src import db


class BaseModel(db.Model):

    """Базовая модель."""

    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, unique=True)


class TimestampMixin:

    """Миксин для временной метки."""

    __abstract__ = True
    created_on = db.Column(db.DateTime, default=datetime.utcnow)


class IsActiveMixin:

    """Миксин для флага активнен."""

    __abstract__ = True
    is_active = db.Column(db.Boolean, default=True)
