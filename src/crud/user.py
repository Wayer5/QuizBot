from typing import Optional

from src import db
from src.crud.base import CRUDBase
from src.models.user import User


class CRUDUser(CRUDBase):

    """Крад класс пользователя."""

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Получение пользователя по логину.

        Keyword Arguments:
        -----------------
        telegram_id (int): тг ид пользователя

        """
        user = db.session.execute(
            db.select(User).where(User.telegram_id == telegram_id),
        )
        return user.scalars().first()


user_crud = CRUDUser(User)
