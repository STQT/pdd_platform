import asyncio
import os
import httpx
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)
from media_cache import media_cache

router = Router()

API_URL = os.environ.get("API_URL", "http://backend:8000/api")
MEDIA_PUBLIC_URL = os.environ.get("MEDIA_PUBLIC_URL", "https://pddtest.leetcode.uz/media")

EXAM_MAX_WRONG = 3


# ── API ───────────────────────────────────────────────────────────────────────

async def api_start_session(category_id: str | None, mode: str) -> dict:
    payload = {"mode": mode}
    if category_id and category_id != "all":
        payload["category_id"] = int(category_id)
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(f"{API_URL}/sessions/", json=payload)
        r.raise_for_status()
        return r.json()


async def api_get_session(session_key: str) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{API_URL}/sessions/{session_key}/")
        r.raise_for_status()
        return r.json()


async def api_get_question(question_id: int) -> dict:
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(f"{API_URL}/questions/{question_id}/")
        r.raise_for_status()
        return r.json()


async def api_submit_answer(session_key: str, question_id: int, answer_id: int) -> dict:
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.post(
            f"{API_URL}/sessions/{session_key}/answer/",
            json={"question_id": question_id, "answer_id": answer_id},
        )
        r.raise_for_status()
        return r.json()


# ── Keyboards ─────────────────────────────────────────────────────────────────

def question_kb(
    answers: list[dict], session_key: str, question_id: int, lang: str
) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=LETTERS[i] if i < len(LETTERS) else str(i + 1),
            callback_data=f"ans:{session_key}:{question_id}:{ans['id']}:{lang}",
        )]
        for i, ans in enumerate(answers)
    ])


def result_kb(
    answers: list[dict],
    correct_id: int,
    selected_id: int,
    session_key: str,
    lang: str,
    include_next: bool = True,
) -> InlineKeyboardMarkup:
    rows = []
    for ans in answers:
        if ans["id"] == correct_id:
            prefix = "✅ "
        elif ans["id"] == selected_id:
            prefix = "❌ "
        else:
            prefix = "◻️ "
        label = ans["text_kz"] if lang == "kz" and ans.get("text_kz") else ans["text_ru"]
        rows.append([InlineKeyboardButton(
            text=f"{prefix}{label[:58]}",
            callback_data=f"noop:{ans['id']}",
        )])
    if include_next:
        next_label = "➡️ Следующий" if lang == "ru" else "➡️ Келесі"
        rows.append([InlineKeyboardButton(
            text=next_label,
            callback_data=f"next:{session_key}:{lang}",
        )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def next_kb(session_key: str, lang: str) -> InlineKeyboardMarkup:
    label = "➡️ Следующий" if lang == "ru" else "➡️ Келесі"
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=label, callback_data=f"next:{session_key}:{lang}")
    ]])


# ── Media ─────────────────────────────────────────────────────────────────────

async def send_video_cached(
    message: Message,
    media_path: str,
    caption: str,
    kb: InlineKeyboardMarkup | None = None,
) -> Message | None:
    """
    Send video using cached file_id (instant) or public URL (first time).
    Saves file_id after first successful upload.
    """
    cached = media_cache.get(media_path)
    src = cached if cached else f"{MEDIA_PUBLIC_URL}/{media_path}"
    try:
        msg = await message.answer_video(
            video=src,
            caption=caption,
            reply_markup=kb,
            parse_mode="HTML",
            supports_streaming=True,
        )
        if not cached and msg.video:
            await media_cache.save(media_path, msg.video.file_id)
        return msg
    except Exception:
        return None


# ── Question / Results rendering ──────────────────────────────────────────────

LETTERS = ["А", "Б", "В", "Г", "Д"]

def fmt_question(q: dict, index: int, total: int, lang: str) -> str:
    text = q["text_kz"] if lang == "kz" and q.get("text_kz") else q["text_ru"]
    lines = [f"❓ <b>Вопрос {index + 1}/{total}</b>\n\n{text}\n"]
    for i, ans in enumerate(q.get("answers", [])):
        ans_text = ans["text_kz"] if lang == "kz" and ans.get("text_kz") else ans["text_ru"]
        letter = LETTERS[i] if i < len(LETTERS) else str(i + 1)
        lines.append(f"<b>{letter})</b> {ans_text}")
    return "\n".join(lines)


async def send_question(message: Message, session: dict, lang: str):
    q = session.get("current_question")
    if not q:
        await send_results(message, session, lang)
        return

    index = session["current_index"]
    total = session["total"]
    caption = fmt_question(q, index, total, lang)
    kb = question_kb(q["answers"], session["session_key"], q["id"], lang)

    media_path = q.get("question_media")
    if media_path:
        sent = await send_video_cached(message, media_path, caption, kb)
        if not sent:
            await message.answer(caption, reply_markup=kb)
    else:
        await message.answer(caption, reply_markup=kb)


async def send_results(message: Message, session: dict, lang: str):
    correct = session["correct_count"]
    total = session["total"]
    status = session["status"]

    if status == "passed":
        emoji, title = "✅", ("Сдали!" if lang == "ru" else "Тапсырдыңыз!")
    elif status == "failed":
        emoji, title = "❌", ("Не сдали" if lang == "ru" else "Тапсырмадыңыз")
    else:
        emoji, title = "🏁", "Завершено"

    pct = round(correct / total * 100) if total else 0
    label_correct = "Правильных" if lang == "ru" else "Дұрыс"
    label_result = "Результат" if lang == "ru" else "Нәтиже"

    text = (
        f"{emoji} <b>{title}</b>\n\n"
        f"{label_correct}: <b>{correct}/{total}</b>\n"
        f"{label_result}: <b>{pct}%</b>"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔄 Заново / Қайта", callback_data="show_categories")],
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")],
    ])
    await message.answer(text, reply_markup=kb)


# ── Handlers ──────────────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("start_exam:"))
async def start_exam_handler(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    cat_id = callback.data.split(":")[1]
    try:
        session = await api_start_session(cat_id, "exam")
    except Exception as e:
        await callback.message.answer(f"Ошибка запуска: {e}")
        return
    await send_question(callback.message, session, "ru")


@router.callback_query(F.data.startswith("start_test:"))
async def start_test_handler(callback: CallbackQuery, bot: Bot):
    await callback.answer()
    parts = callback.data.split(":")
    cat_id, mode, lang = parts[1], parts[2], parts[3]
    try:
        session = await api_start_session(cat_id, mode)
    except Exception as e:
        await callback.message.answer(f"Ошибка запуска: {e}")
        return
    await send_question(callback.message, session, lang)


@router.callback_query(F.data.startswith("ans:"))
async def answer_handler(callback: CallbackQuery, bot: Bot):
    # Format: ans:{session_key}:{question_id}:{answer_id}:{lang}
    parts = callback.data.split(":")
    session_key = parts[1]
    question_id = int(parts[2])
    answer_id = int(parts[3])
    lang = parts[4] if len(parts) > 4 else "ru"

    await callback.answer()

    try:
        result, question = await asyncio.gather(
            api_submit_answer(session_key, question_id, answer_id),
            api_get_question(question_id),
        )
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
        return

    is_correct: bool = result["is_correct"]
    correct_id: int = result["correct_answer_id"]
    session: dict = result["session"]

    is_training = session.get("mode") == "training"

    # Edit keyboard to reveal correct / wrong answer (no Next button in training — it goes on explanation)
    kb = result_kb(question["answers"], correct_id, answer_id, session_key, lang,
                   include_next=not is_training)
    try:
        await callback.message.edit_reply_markup(reply_markup=kb)
    except Exception:
        pass

    # Feedback popup
    await callback.answer(
        "✅ Правильно!" if is_correct else "❌ Неправильно",
        show_alert=False,
    )

    # Explanation (training mode only) — Next button attached here
    if is_training:
        expl_text = result.get("explanation_kz" if lang == "kz" else "explanation_ru") or ""
        expl_video = result.get("explanation_media") or ""
        expl2_video = result.get("explanation2_media") or ""
        header = "💡 Объяснение" if lang == "ru" else "💡 Түсіндірме"
        nxt = next_kb(session_key, lang) if session["status"] == "active" else None
        if expl_text or expl_video:
            caption = f"<b>{header}</b>" + (f"\n\n{expl_text}" if expl_text else "")
            if expl_video:
                # Next button on last explanation video
                last_kb = nxt if not expl2_video else None
                await send_video_cached(callback.message, expl_video, caption, last_kb)
            elif expl_text:
                last_kb = nxt if not expl2_video else None
                await callback.message.answer(caption, reply_markup=last_kb, parse_mode="HTML")
        if expl2_video:
            await send_video_cached(callback.message, expl2_video, "", nxt)
        elif not (expl_text or expl_video) and nxt:
            # No explanation at all — show Next button as plain message
            next_label = "➡️ Следующий вопрос" if lang == "ru" else "➡️ Келесі сұрақ"
            await callback.message.answer(next_label, reply_markup=nxt)

    # Session finished → show results
    if session["status"] != "active":
        await send_results(callback.message, session, lang)


@router.callback_query(F.data.startswith("next:"))
async def next_handler(callback: CallbackQuery, bot: Bot):
    # Format: next:{session_key}:{lang}
    parts = callback.data.split(":")
    session_key, lang = parts[1], parts[2]
    await callback.answer()

    try:
        session = await api_get_session(session_key)
    except Exception as e:
        await callback.message.answer(f"Ошибка: {e}")
        return

    if session["status"] != "active":
        await send_results(callback.message, session, lang)
        return

    await send_question(callback.message, session, lang)


@router.callback_query(F.data.startswith("noop:"))
async def noop_handler(callback: CallbackQuery):
    await callback.answer()
