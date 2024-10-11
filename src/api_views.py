from http import HTTPStatus

from aiogram.types import Update
from flask import Response, request

from settings import settings

from . import app, bot


@app.post(settings.WEBHOOK_PATH)
async def webhook() -> None:
    """Получаем от тг обновления и передаем в бота."""
    app.logger.info('Webhook called')
    update: Update = Update.model_validate(
        request.get_json(),
        context={'bot': bot.bot},
    )
    await bot.dp.feed_update(bot.bot, update)
    return Response(status=HTTPStatus.OK)
