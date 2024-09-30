from src.crud.base import CRUDBase
from src.models import Category


class CRUDCategory(CRUDBase):
    """Круд класс для рубрик."""


category_crud = CRUDCategory(Category)
