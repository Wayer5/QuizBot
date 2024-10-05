import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

# from aiogram import types
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from settings import settings

from .user_check import check_user_and_clear_messages
from src.crud.telegram_user import telegram_user_crud

# from .models import TelegramUser, db
from src.crud.user import user_crud

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объект бота. https://t.me/MedStatSolution_Bot
bot: Bot = Bot(
    token=settings.TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# Диспетчер
dp: Dispatcher = Dispatcher()


def create_reply_keyboard() -> ReplyKeyboardMarkup:
    """Функция для создания Reply клавиатуры с кнопкой 'Start'.

    Returns
    -------
    ReplyKeyboardMarkup
        Клавиатура с кнопкой 'Start'.

    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Start')],
        ],
        resize_keyboard=True,
    )


@dp.message(Command('start'))
async def cmd_start(message: Message) -> None:
    """Отправка приветствия и кнопки 'Start'.

    Args:
    ----
        message (Message): Входящее сообщение.

    """
    tg_user = message.from_user
    tg_user_id = tg_user.id
    user = await user_crud.get_by_telegram_id(tg_user_id)
    if user is None:
        name = tg_user.full_name
        username = tg_user.username
        tg_user_id = tg_user.id
        is_admin = user_crud.get_multi() == []
        user_crud.create(
            {
                'name': name,
                'username': username,
                'telegram_id': tg_user_id,
                'is_admin': is_admin,
            },
        )
        logging.info(
            f'Пользователь {name} ({username}) зарегистрирован в боте.',
        )

    if not telegram_user_crud.exists_by_telegram_id(tg_user.id):
        username = tg_user.username
        first_name = tg_user.first_name
        last_name = tg_user.last_name
        is_premium = tg_user.is_premium
        added_to_attachment_menu = tg_user.added_to_attachment_menu
        language_code = tg_user.language_code

        telegram_user_crud.create(
            {
                'telegram_id': tg_user_id,
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'language_code': language_code,
                'is_premium': is_premium,
                'added_to_attachment_menu': added_to_attachment_menu,
            },
        )
        logging.info(
            f'Пользователь {tg_user_id} зарегистрирован в TelegramUser.')

    # Отправляем приветственное сообщение с кнопкой 'Start'
    await message.answer(
        'Привет, Я МедСтатбот! Нажми кнопку "Start", чтобы продолжить.',
        reply_markup=create_reply_keyboard(),
    )


@dp.message(lambda message: message.text == 'Start')
async def on_start_button(message: Message) -> None:
    """Обработка нажатия кнопки 'Start' и отправка WebApp кнопки.

    Args:
    ----
        message (Message): Входящее сообщение.

    """
    web_app_url: str = settings.WEB_URL

    if not await check_user_and_clear_messages(bot, message):  # Передаем bot
        return  # Завершаем, если пользователь не активен

    web_app_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Квиз',
        web_app=WebAppInfo(url=web_app_url),
    )

    admin_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Админка',
        web_app=WebAppInfo(url=web_app_url + '/auth'),
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])
    user = await user_crud.get_by_telegram_id(message.from_user.id)
    if user.is_admin and user.is_active:
        keyboard.inline_keyboard[0].append(admin_button)

    if user.is_active:
        # Отправляем инлайн-кнопку для открытия WebApp
        msg = await message.answer(  # Сохраняем сообщение
            'Нажми кнопку ниже, чтобы открыть WebApp:',
            reply_markup=keyboard,
        )

        if not user.is_admin:
            # Удаляем сообщение с кнопкой через 5 минут (300 секунд)
            await asyncio.sleep(10)  # Задержка 5 минут
            await bot.delete_message(message.from_user.id, msg.message_id)
    else:
        await message.answer(
            'Вы были заблокированы. Обратитесь к администратору.',
        )
