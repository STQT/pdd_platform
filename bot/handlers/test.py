import os
import httpx
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

router = Router()

API_URL = os.environ.get("API_URL", "http://backend:8000/api")
MEDIA_BASE = os.environ.get("MEDIA_BASE_URL", "http://backend:8000/media")


async def start_session(category_id: str | None, mode: str) -> dict:
    payload = {"mode": mode}
    if category_id and category_id != "all":
        payload["category_id"] = int(category_id)
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{API_URL}/sessions/", json=payload)
        resp.raise_for_status()
        return resp.json()


async def submit_answer(session_key: str, question_id: int, answer_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{API_URL}/sessions/{session_key}/answer/",
            json={"question_id": question_id, "answer_id": answer_id},
        )
        resp.raise_for_status()
        return resp.json()


def question_kb(answers: list[dict], session_key: str, question_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    buttons = []
    for ans in answers:
        text = ans["text_kz"] if lang == "kz" and ans.get("text_kz") else ans["text_ru"]
        buttons.append([
            InlineKeyboardButton(
                text=text[:60],
                callback_data=f"answer:{session_key}:{question_id}:{ans['id']}:{lang}",
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def format_question(q: dict, index: int, total: int, lang: str = "ru") -> str:
    text = q["text_kz"] if lang == "kz" and q.get("text_kz") else q["text_ru"]
    return f"❓ <b>Вопрос {index + 1}/{total}</b>\n\n{text}"


@router.callback_query(F.data.startswith("start_exam:"))
async def start_exam(callback: CallbackQuery):
    await callback.answer()
    cat_id = callback.data.split(":")[1]
    await _begin_session(callback, cat_id, "exam", "ru")


@router.callback_query(F.data.startswith("start_test:"))
async def start_test(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    cat_id, mode, lang = parts[1], parts[2], parts[3]
    await _begin_session(callback, cat_id, mode, lang)


async def _begin_session(callback: CallbackQuery, cat_id: str, mode: str, lang: str):
    try:
        session = await start_session(cat_id, mode)
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
        return

    await _send_question(callback.message, session, lang, edit=True)


async def _send_question(message, session: dict, lang: str, edit: bool = False):
    q = session.get("current_question")
    if not q:
        await _send_results(message, session, lang, edit=edit)
        return

    index = session["current_index"]
    total = session["total"]
    text = format_question(q, index, total, lang)
    kb = question_kb(q["answers"], session["session_key"], q["id"], lang)

    media_path = q.get("question_media")
    if media_path:
        media_url = f"{MEDIA_BASE}/{media_path}"
        video_text = text + f'\n\n<a href="{media_url}">▶ Видео</a>'
        if edit:
            await message.edit_text(video_text, reply_markup=kb)
        else:
            await message.answer(video_text, reply_markup=kb)
    else:
        if edit:
            await message.edit_text(text, reply_markup=kb)
        else:
            await message.answer(text, reply_markup=kb)


async def _send_results(message, session: dict, lang: str, edit: bool = False):
    correct = session["correct_count"]
    total = session["total"]
    status = session["status"]

    if status == "passed":
        emoji = "✅"
        result_text = "Сдали!" if lang == "ru" else "Тапсырдыңыз!"
    elif status == "failed":
        emoji = "❌"
        result_text = "Не сдали" if lang == "ru" else "Тапсырмадыңыз"
    else:
        emoji = "🏁"
        result_text = "Завершено"

    text = (
        f"{emoji} <b>{result_text}</b>\n\n"
        f"Правильных ответов: <b>{correct}/{total}</b>\n"
        f"Процент: <b>{round(correct/total*100) if total else 0}%</b>"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Ещё раз", callback_data="main_menu")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])

    if edit:
        await message.edit_text(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data.startswith("answer:"))
async def handle_answer(callback: CallbackQuery):
    await callback.answer()
    parts = callback.data.split(":")
    # answer:{session_key}:{question_id}:{answer_id}:{lang}
    session_key = parts[1]
    question_id = int(parts[2])
    answer_id = int(parts[3])
    lang = parts[4] if len(parts) > 4 else "ru"

    try:
        result = await submit_answer(session_key, question_id, answer_id)
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
        return

    is_correct = result["is_correct"]
    session = result["session"]

    # Show feedback for training mode
    if session["mode"] == "training":
        if is_correct:
            feedback = "✅ Правильно!"
        else:
            correct_id = result.get("correct_answer_id")
            feedback = f"❌ Неправильно."

        # Quick inline notification
        await callback.answer(feedback, show_alert=False)

    await _send_question(callback.message, session, lang, edit=True)
