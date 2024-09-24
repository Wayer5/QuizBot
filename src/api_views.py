from http import HTTPStatus
from aiogram.types import Update
from flask import request, Response

from . import app, bot
from settings import settings


@app.post(settings.WEBHOOK_PATH)  # type: ignore[misc]
async def webhook() -> None:
    """
    Handle incoming Telegram updates by putting
    them into the `update_queue`
    """
    update: Update = Update.model_validate(
        request.get_json(), context={'bot': bot.bot}
    )
    await bot.dp.feed_update(bot.bot, update)
    return Response(status=HTTPStatus.OK)
