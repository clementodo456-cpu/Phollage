from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from keyboards.templates import get_templates_keyboard
from services.session_manager import session_manager

router = Router()

TEMPLATES_INFO = (
    "<b>🎨 Available Collage Templates:</b>\n\n"
    "• <b>Classic Grid:</b> Uniform balanced photo layout.\n"
    "• <b>Masonry:</b> Pinterest-style adaptive multi-column arrangement.\n"
    "• <b>Magazine:</b> Large main feature image with sub-photos.\n"
    "• <b>Film Strip:</b> Sequential horizontal/vertical strip layout.\n"
    "• <b>Polaroid:</b> Modern photo card styled layout.\n"
    "• <b>2x2 / 3x3 Grid:</b> Precision grids for 4 or 9 photos.\n"
    "• <b>Story:</b> Full portrait layout styled for mobile stories."
)

@router.message(Command("templates"))
@router.callback_query(F.data == "cmd_templates")
async def templates_handler(event: Message | CallbackQuery):
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(TEMPLATES_INFO, parse_mode="HTML", reply_markup=get_templates_keyboard())
        await event.answer()
    else:
        await event.answer(TEMPLATES_INFO, parse_mode="HTML", reply_markup=get_templates_keyboard())

@router.callback_query(F.data == "flow_templates")
async def flow_templates_callback(callback: CallbackQuery):
    session = await session_manager.get_or_create(callback.from_user.id)
    current = session.get("template", "Classic Grid")
    await callback.message.edit_text(
        "<b>🎨 Choose a Template Layout:</b>",
        parse_mode="HTML",
        reply_markup=get_templates_keyboard(current)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("set_template_"))
async def set_template_callback(callback: CallbackQuery):
    template_name = callback.data.replace("set_template_", "")
    await session_manager.update_settings(callback.from_user.id, "template", template_name)
    await callback.answer(f"Template set to {template_name}")
    
    session = await session_manager.get_or_create(callback.from_user.id)
    await callback.message.edit_text(
        f"<b>🎨 Selected Template:</b> {template_name}\n\n"
        "You can now customize styling options or proceed to generation.",
        parse_mode="HTML",
        reply_markup=get_templates_keyboard(template_name)
    )
