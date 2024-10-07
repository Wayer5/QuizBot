from sqlalchemy import select, true

from src import db
from src.crud.base import CRUDBase
from src.models import Category


class CRUDCategory(CRUDBase):

    """Круд класс для рубрик."""

    def get_active(self, is_active: bool = true()) -> list[Category]:
        """Получить все активные рубрики."""
        return (
            db.session.execute(
                select(Category).where(Category.is_active == is_active),
            )
            .scalars()
            .all()
        )


category_crud = CRUDCategory(Category)
