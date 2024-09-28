import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)

from settings import settings

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
    username = tg_user.username
    user = await user_crud.get_by_username(username)
    if user is None:
        name = tg_user.full_name
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

    web_app_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Квиз',
        web_app=WebAppInfo(url=web_app_url),
    )

    admin_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Админка',
        web_app=WebAppInfo(url=web_app_url + '/auth'),
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])
    user = await user_crud.get_by_username(message.from_user.username)
    if user.is_admin:
        keyboard.inline_keyboard[0].append(admin_button)

    # Отправляем инлайн-кнопку для открытия WebApp
    await message.answer(
        'Нажми кнопку ниже, чтобы открыть WebApp:',
        reply_markup=keyboard,
    )
