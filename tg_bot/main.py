import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode

from tg_bot.core.config import settings
from tg_bot.core.logger import setup_logging
from tg_bot.domain.handlers import register_handlers
from tg_bot.middlewares import AccessMiddleware


async def main() -> None:
    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()
    dp.update.middleware(AccessMiddleware())
    register_handlers(dp)

    await dp.start_polling(bot)


if __name__ == "__main__":
    setup_logging()
    print("Запуск бота")
    logging.info("Запуск бота")
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот остановлен")
