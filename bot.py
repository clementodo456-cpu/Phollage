import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from handlers import start, help, templates, photos, collage
from utils.cleanup import periodic_session_cleanup

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # Include Routers
    dp.include_routers(
        start.router,
        help.router,
        templates.router,
        collage.router,
        photos.router
    )

    # Start background cleanup loop
    cleanup_task = asyncio.create_task(periodic_session_cleanup())

    logger.info("Phollagebot starts polling...")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        cleanup_task.cancel()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
