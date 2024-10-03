from src.crud.base import CRUDBase
from src.models import UserAnswer


class CRUDUserAnswer(CRUDBase):

    """Круд класс для ответов."""


user_answer_crud = CRUDUserAnswer(UserAnswer)
