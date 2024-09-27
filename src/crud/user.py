from typing import Optional

from src import db
from src.crud.base import CRUDBase
from src.models import User


class CRUDUser(CRUDBase):
    async def get_id_by_username(self, username: str) -> Optional[User]:
        user_id = db.session.execute(
            db.select(User.id).where(User.username == username)
        )
        return user_id.scalars().first()


user_crud = CRUDUser(User)
