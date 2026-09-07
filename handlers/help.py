from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.main import get_start_keyboard

router = Router()

HELP_TEXT = (
    "<b>📖 How to Use Phollagebot:</b>\n\n"
    "1️⃣ Send /collage or click <b>Create Collage</b>.\n"
    "2️⃣ Upload between <b>2 and 20 photos</b>.\n"
    "3️⃣ (Optional) Click <b>Arrange Photos</b> to change photo order.\n"
    "4️⃣ Pick a layout template & aspect ratio format.\n"
    "5️⃣ Customize borders, corner rounding, spacing, and add titles.\n"
    "6️⃣ Hit <b>Generate Collage</b> to receive your HD collage!\n\n"
    "<b>Commands:</b>\n"
    "• /start - Welcome menu\n"
    "• /collage - Start new collage session\n"
    "• /templates - View layout options\n"
    "• /clear - Reset current session\n"
    "• /help - Usage guide"
)

@router.message(Command("help"))
@router.callback_query(F.data == "cmd_help")
async def help_handler(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(HELP_TEXT, parse_mode="HTML", reply_markup=get_start_keyboard())
        await event.answer()
    else:
        await event.answer(HELP_TEXT, parse_mode="HTML", reply_markup=get_start_keyboard())
