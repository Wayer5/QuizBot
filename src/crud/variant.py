from src.crud.base import CRUDBase
from src.models.variant import Variant


class CRUDVariant(CRUDBase):

    """Круд класс для вариантов ответа."""


variant_crud = CRUDVariant(Variant)
