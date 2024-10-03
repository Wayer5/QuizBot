from src.crud.base import CRUDBase
from src.models import QuizResult


class CRUDQuizResult(CRUDBase):

    """Круд класс для результатов квиза."""


quiz_result_crud = CRUDQuizResult(QuizResult)
