import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message

from app.core.config import settings
from app.core.logging_conf import setup_logging
from app.tg_prepare_message import STARTUP_TEXT
from app.nlp_sql import natural_language_to_sql
from app.sql_executor import run_sql_and_get_number

setup_logging()
logger = logging.getLogger(__name__)


async def cmd_start(message: Message):
    await message.answer(STARTUP_TEXT)


async def handle_message(message: Message):
    text = message.text or ""
    if not text.strip():
        await message.answer("Отправь, пожалуйста, текстовый запрос.")
        return

    try:
        # ненерируем SQL через ИИ
        sql = natural_language_to_sql(text)

        # выполняем SQL (асинхронно)
        result = await run_sql_and_get_number(sql)


        if not isinstance(result, (int, float)):
            raise ValueError("Result is not numeric")

        await message.answer(str(result))
    except Exception as e:
        logger.exception("Error while handling message: %s", e)
        await message.answer("Не смог понять или посчитать твой запрос(")


async def main():
    token = settings.bot.telegram_bot_token
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set")

    bot = Bot(token=token)
    dp = Dispatcher()

    dp.message.register(cmd_start, CommandStart())
    dp.message.register(handle_message, F.text)

    logger.info("Starting bot polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
