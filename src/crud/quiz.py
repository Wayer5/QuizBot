from src import db
from src.crud.base import CRUDBase
from src.models import Quiz


class CRUDQuiz(CRUDBase):

    """Круд класс викторин."""

    def get_by_category_id(self, category_id: int) -> list[Quiz]:
        """Получение викторин по id категории."""
        quizzes = db.session.execute(
            db.select(Quiz).where(Quiz.category_id == category_id),
        )
        return quizzes.scalars().all()


quiz_crud = CRUDQuiz(Quiz)
