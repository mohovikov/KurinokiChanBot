import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from core import config
from core.services import UserService
from core.callbacks import setup as setup_handlers_routers
from core.handlers import setup as setup_callback_routers
from core.middlewares import UserLoggerMiddleware

logger = logging.getLogger(__name__)


async def main() -> None:
    await config.show_logo()
    bot = Bot(
        token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    await UserService.sync_bot_user(bot)

    dp.message.outer_middleware(UserLoggerMiddleware())
    logger.info("🔌 Middleware подключён")

    dp.include_router(setup_handlers_routers())
    dp.include_router(setup_callback_routers())

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    config.setup_logging()
    logger.debug("⚠️ Внимание! Бот запущен в DEBUG режиме!")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 Каштанчик остановлен вручную")
    except Exception as e:
        logger.critical(f"💥 Критическая ошибка: {e}", exc_info=True)
