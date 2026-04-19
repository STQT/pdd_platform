import asyncio
import logging
import os
import httpx
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ChatMemberStatus
from aiogram.client.default import DefaultBotProperties
from aiogram.types import ChatMemberUpdated
from handlers import start, categories, test

load_dotenv()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

BOT_TOKEN = os.environ["BOT_TOKEN"]
API_URL = os.environ.get("API_URL", "http://backend:8000/api")


async def on_user_blocked(event: ChatMemberUpdated):
    chat_id = event.from_user.id
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(f"{API_URL}/tg-users/{chat_id}/block/")
    except Exception as e:
        log.warning("Failed to deactivate user %s: %s", chat_id, e)


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.my_chat_member.register(
        on_user_blocked,
        F.new_chat_member.status == ChatMemberStatus.KICKED,
    )

    dp.include_router(start.router)
    dp.include_router(categories.router)
    dp.include_router(test.router)

    log.info("Bot starting...")
    await dp.start_polling(bot, allowed_updates=["message", "callback_query", "my_chat_member"])


if __name__ == "__main__":
    asyncio.run(main())
