from src.crud.base import CRUDBase
from src.models import Variant


class CRUDVariant(CRUDBase):

    """Круд класс для вариантов ответа."""


quiz_result_crud = CRUDVariant(Variant)
