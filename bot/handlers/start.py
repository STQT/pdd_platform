import os
import logging
import httpx
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
log = logging.getLogger(__name__)

API_URL = os.environ.get("API_URL", "http://backend:8000/api")


async def register_user(user) -> None:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            await client.post(f"{API_URL}/tg-users/", json={
                "chat_id": user.id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
            })
    except Exception as e:
        log.warning("Failed to register user %s: %s", user.id, e)

WELCOME_RU = (
    "👋 <b>Добро пожаловать в PDD Test Bot!</b>\n\n"
    "Здесь вы можете подготовиться к экзамену ПДД Казахстана.\n\n"
    "Выберите действие:"
)
WELCOME_KZ = (
    "👋 <b>PDD Test Bot-қа қош келдіңіз!</b>\n\n"
    "Мұнда Қазақстан ЖҚЕ емтиханына дайындала аласыз.\n\n"
    "Әрекетті таңдаңыз:"
)


def main_menu_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📚 Категории / Санаттар", callback_data="show_categories"),
        ],
        [
            InlineKeyboardButton(text="🎯 Экзамен (20 вопросов)", callback_data="start_exam:all"),
        ],
        [
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang:kz"),
        ],
    ])


@router.message(CommandStart())
async def cmd_start(message: Message):
    await register_user(message.from_user)
    await message.answer(WELCOME_RU, reply_markup=main_menu_kb())
