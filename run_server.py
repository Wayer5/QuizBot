import asyncio
import logging

import uvicorn
from asgiref.wsgi import WsgiToAsgi

from settings import settings

from src import app, bot


async def main() -> None:
    """Стартуем сервер и бота."""
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=WsgiToAsgi(app),
            port=settings.PORT,
            use_colors=False,
            host="0.0.0.0",
        ),
    )

    await bot.bot.set_webhook(
        url=settings.WEBHOOK_URL,
        allowed_updates=bot.dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    logging.info('Бот запущен')
    await webserver.serve()
    await bot.bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.error('Бот остановлен')
