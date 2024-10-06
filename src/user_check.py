# user_check.py

import logging

from aiogram import Bot
from aiogram.types import Message

from src.crud.user import user_crud


async def check_user_and_clear_messages(bot: Bot, message: Message) -> bool:
    """Проверка пользователя и очистка предыдущих сообщений в чате.

    Returns
    -------
    bool
        True, если пользователь активен, иначе False.

    """
    tg_user_id = message.from_user.id
    user = await user_crud.get_by_telegram_id(tg_user_id)

    if user is None or not user.is_active:
        """Проверка на удаление юзера."""
        # Очищаем предыдущие сообщения в чате
        try:
            for message_id in range(
                message.message_id, message.message_id - 10, -1,
            ):
                await bot.delete_message(
                    chat_id=message.chat.id, message_id=message_id,
                )
        except Exception as e:
            logging.warning(f"Не удалось удалить сообщение: {e}")

        # Уведомляем пользователя о повторной регистрации и убираем кнопки
        await message.answer(
            'Вас нет в базе или вы удалены. Введите /start для регистрации.',
            reply_markup=None,  # Убираем кнопки
        )
        return False  # Пользователь не активен

    return True  # Пользователь активен
