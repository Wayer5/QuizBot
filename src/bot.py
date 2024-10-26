import emoji
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

from . import app
from .constants import BAN_WARN_MESSAGE
from .crud.telegram_user import telegram_user_crud
from .crud.user import user_crud
from src.settings import settings

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
        Клавиатура с кнопкой 'Продолжить'.

    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Продолжить')],
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
        app.logger.info(
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
        app.logger.info(
            f'Пользователь {tg_user_id} зарегистрирован в TelegramUser.',
        )

    # Отправляем приветственное сообщение с кнопкой 'Start'
    await message.answer(
        (
            f'👋 Привет, {tg_user.first_name}!\n'
            f'Мы рады видеть тебя у нас в боте{emoji.emojize(":robot:")}!\n'
            'Нажми кнопку ⬇️, чтобы продолжить.'
        ),
        reply_markup=create_reply_keyboard(),
    )


@dp.message(lambda message: message.text == 'Продолжить')
async def on_start_button(message: Message) -> None:
    """Обработка нажатия кнопки 'Start' и отправка WebApp кнопки.

    Args:
    ----
        message (Message): Входящее сообщение.

    """
    user = await user_crud.get_by_telegram_id(message.from_user.id)
    if user is None or not user.is_active:
        # Уведомляем пользователя о бане или повторной регистрации
        await message.answer(
            BAN_WARN_MESSAGE,
            reply_markup=None,  # Убираем кнопки
        )
        return
    web_app_url: str = settings.WEB_URL

    web_app_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Викторина',
        web_app=WebAppInfo(url=web_app_url),
    )

    admin_button: InlineKeyboardButton = InlineKeyboardButton(
        text='Админка',
        web_app=WebAppInfo(url=web_app_url + '/auth'),
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[[web_app_button]])
    if user.is_admin:
        keyboard.inline_keyboard[0].append(admin_button)

    # Отправляем инлайн-кнопку для открытия WebApp
    await message.answer(
        'Нажми кнопку Викторина⬇️, чтобы открыть приложение!',
        reply_markup=keyboard,
    )
