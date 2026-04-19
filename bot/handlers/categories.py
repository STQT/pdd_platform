import os
import httpx
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

API_URL = os.environ.get("API_URL", "http://backend:8000/api")


async def fetch_categories() -> list[dict]:
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{API_URL}/categories/")
        resp.raise_for_status()
        return resp.json()["results"] if "results" in resp.json() else resp.json()


def categories_kb(cats: list[dict], lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    for cat in cats:
        title = cat["title_kz"] if lang == "kz" and cat.get("title_kz") else cat["title_ru"]
        count = cat.get("question_count", 0)
        buttons.append([
            InlineKeyboardButton(
                text=f"{title} ({count})",
                callback_data=f"category:{cat['id']}:{lang}",
            )
        ])
    buttons.append([InlineKeyboardButton(text="« Назад / Артқа", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router.callback_query(F.data == "show_categories")
async def show_categories(callback: CallbackQuery):
    await callback.answer()
    cats = await fetch_categories()
    await callback.message.edit_text(
        "📚 <b>Выберите категорию:</b>",
        reply_markup=categories_kb(cats),
    )


@router.callback_query(F.data.startswith("category:"))
async def select_category(callback: CallbackQuery):
    await callback.answer()
    _, cat_id, lang = callback.data.split(":")
    await callback.message.edit_text(
        f"Выберите режим:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(
                text="📖 Обучение (все вопросы)",
                callback_data=f"start_test:{cat_id}:training:{lang}",
            )],
            [InlineKeyboardButton(
                text="🎯 Экзамен (20 вопросов)",
                callback_data=f"start_test:{cat_id}:exam:{lang}",
            )],
            [InlineKeyboardButton(text="« Назад", callback_data="show_categories")],
        ]),
    )


@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    from .start import main_menu_kb, WELCOME_RU
    await callback.answer()
    await callback.message.edit_text(WELCOME_RU, reply_markup=main_menu_kb())
