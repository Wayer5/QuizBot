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

from .models import TelegramUser, db

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объект бота. https://t.me/MedStatSolution_Bot
bot: Bot = Bot(token=settings.TELEGRAM_TOKEN,
               default=DefaultBotProperties(parse_mode=ParseMode.HTML))

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


def create_inline_keyboard(web_app_url: str) -> InlineKeyboardMarkup:
    """Функция для создания Inline клавиатуры с WebApp кнопкой.

    Args:
    ----
    web_app_url : str
        URL веб-приложения для кнопки.

    Returns:
    -------
    InlineKeyboardMarkup
        Инлайн-клавиатура с WebApp кнопкой.

    """
    web_app_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Открыть WebApp',  # Текст кнопки
        web_app=WebAppInfo(url=web_app_url),  # URL веб-приложения
    )
    return InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])


@dp.message(Command('start'))
async def cmd_start(message: Message) -> None:
    """Отправка приветствия и кнопки 'Start'.

    Args:
    ----
        message (Message): Входящее сообщение.

    """
    user = message.from_user

    existing_user = TelegramUser.query.filer_by(telegram_id=user.id).first()
    if not existing_user:
        new_user = TelegramUser(
            telegram_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            language_code=user.language_codem,
            is_premium=user.is_premium,
            added_to_attachment_menu=user.added_to_attachment_menu,
        )
        db.session.add(new_user)
        db.session.commit()
        logging.info(f"Новый пользователь добавлен: {user.id}")

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
    web_app_url: str = 'https://ya-workshop.kaiten.ru/space/440575'

    # Отправляем инлайн-кнопку для открытия WebApp
    await message.answer(
        'Нажми кнопку ниже, чтобы открыть WebApp:',
        reply_markup=create_inline_keyboard(web_app_url),
    )
