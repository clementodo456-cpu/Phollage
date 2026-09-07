from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from keyboards.main import get_start_keyboard
from services.session_manager import session_manager

router = Router()

START_TEXT = (
    "<b>Welcome to Phollagebot!</b> 🖼✨\n\n"
    "I am your professional photo collage studio inside Telegram. "
    "Upload photos, reorder them, select canvas formats, apply beautiful "
    "borders, spacing, rounded corners, and captions with ease.\n\n"
    "👇 Choose an option below to get started:"
)

@router.message(CommandStart())
async def cmd_start_handler(message: Message):
    await message.answer(START_TEXT, parse_mode="HTML", reply_markup=get_start_keyboard())

@router.message(Command("about"))
@router.callback_query(F.data == "cmd_about")
async def about_handler(event: Message | CallbackQuery):
    text = (
        "<b>ℹ️ About Phollagebot</b>\n\n"
        "Phollagebot is a high-performance Telegram bot built with Python, "
        "aiogram 3.x, and Pillow. It generates high-resolution custom photo "
        "collages on demand without storing your photos permanently.\n\n"
        "<b>Privacy First:</b> Your photos are stored temporarily in memory during "
        "editing and deleted immediately when done or expired."
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML", reply_markup=get_start_keyboard())
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML", reply_markup=get_start_keyboard())
