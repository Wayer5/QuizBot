from flask import abort
from sqlalchemy import select, true

from src import db
from src.constants import HTTP_NOT_FOUND
from src.crud.base import CRUDBase
from src.models import Category


class CRUDCategory(CRUDBase):

    """Круд класс для рубрик."""

    def get_active(self, is_active: bool = true()) -> list[Category]:
        """Получить все активные рубрики."""
        categories = (
            db.session.execute(
                select(Category).where(Category.is_active == is_active),
            )
            .scalars()
            .all()
        )
        if not categories:
            abort(HTTP_NOT_FOUND)
        return categories


category_crud = CRUDCategory(Category)
