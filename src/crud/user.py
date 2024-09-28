from typing import Optional

from src import db
from src.crud.base import CRUDBase
from src.models import User


class CRUDUser(CRUDBase):

    """Крад класс пользователя."""

    async def get_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по логину.

        Keyword Arguments:
        username (str): Логин пользователя.

        """
        user = db.session.execute(
            db.select(User).where(User.username == username),
        )
        return user.scalars().first()


user_crud = CRUDUser(User)
