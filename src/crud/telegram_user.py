from typing import Optional

from src import db
from src.crud.base import CRUDBase
from src.models.telegram_user import TelegramUser


class CRUDTelegramUser(CRUDBase):

    """Класс для работы с моделью TelegramUser через CRUD."""

    async def get_by_telegram_id(
        self, telegram_id: int,
    ) -> Optional[TelegramUser]:
        """Получение пользователя по telegram_id."""
        return (
            db.session.execute(
                db.select(TelegramUser).where(
                    TelegramUser.telegram_id == telegram_id,
                ),
            )
            .scalars()
            .first()
        )

    async def exists_by_telegram_id(self, telegram_id: int) -> bool:
        """Проверка существования пользователя по telegram_id."""
        return db.session.query(
            db.exists().where(TelegramUser.telegram_id == telegram_id),
        ).scalar()


telegram_user_crud = CRUDTelegramUser(TelegramUser)
