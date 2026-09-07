from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from config import MIN_PHOTOS
from services.session_manager import session_manager
from services.collage_engine import CollageEngine
from keyboards.collage import (
    get_upload_keyboard, get_customize_keyboard,
    get_options_keyboard, get_preview_keyboard, get_finished_keyboard
)
from handlers.photos import PhotoUploadState

router = Router()

@router.message(Command("collage"))
@router.callback_query(F.data == "cmd_create")
async def start_collage_handler(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    user_id = event.from_user.id
    await session_manager.clear(user_id)
    session = await session_manager.get_or_create(user_id)

    text = (
        "🖼 <b>Create a New Collage</b>\n\n"
        "Please send <b>2 to 20 photos</b> directly in this chat.\n"
        "You can send them one by one or all together as a batch."
    )
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, parse_mode="HTML")
        await event.answer()
    else:
        await event.answer(text, parse_mode="HTML")

@router.message(Command("clear"))
@router.callback_query(F.data == "action_clear")
async def clear_session_handler(event: Message | CallbackQuery, state: FSMContext):
    await state.clear()
    await session_manager.clear(event.from_user.id)
    text = "🗑 Session cleared. Send /collage to start fresh."
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text)
        await event.answer()
    else:
        await event.answer(text)

@router.callback_query(F.data == "action_cancel")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("❌ Action cancelled. Send /start to view options.")
    await callback.answer()

@router.callback_query(F.data == "flow_continue")
@router.callback_query(F.data == "flow_customize")
async def flow_customize_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    session = await session_manager.get_or_create(callback.from_user.id)
    if len(session.get("photos", [])) < MIN_PHOTOS:
        await callback.answer(f"Please upload at least {MIN_PHOTOS} photos first.", show_alert=True)
        return

    await callback.message.edit_text(
        "🎨 <b>Collage Customization Studio</b>\n\nAdjust layout options below:",
        parse_mode="HTML",
        reply_markup=get_customize_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data.startswith("opt_"))
async def options_menu_callback(callback: CallbackQuery, state: FSMContext):
    option_type = callback.data.replace("opt_", "")
    
    if option_type == "caption":
        await state.set_state(PhotoUploadState.waiting_for_caption)
        await callback.message.edit_text(
            "📝 Send the caption text you want on your collage, or click /cancel to keep empty:"
        )
        await callback.answer()
        return

    session = await session_manager.get_or_create(callback.from_user.id)
    current_val = session.get(
        "border_color" if option_type == "border_color" else option_type, ""
    )

    titles = {
        "format": "📐 Choose Canvas Aspect Ratio:",
        "border": "🔲 Choose Border Width:",
        "border_color": "🎨 Choose Border Color:",
        "corner": "📐 Choose Corner Style:",
        "spacing": "↔️ Choose Photo Spacing:",
        "bg": "🖼 Choose Background Color:"
    }

    await callback.message.edit_text(
        titles.get(option_type, "Select Option:"),
        reply_markup=get_options_keyboard(option_type, current_val)
    )
    await callback.answer()

@router.message(PhotoUploadState.waiting_for_caption)
async def process_caption_input(message: Message, state: FSMContext):
    caption = message.text.strip() if message.text else ""
    await session_manager.update_settings(message.from_user.id, "caption", caption)
    await state.clear()
    await message.answer(
        f"✅ Caption saved: <i>\"{caption}\"</i>" if caption else "✅ Caption removed.",
        parse_mode="HTML",
        reply_markup=get_customize_keyboard()
    )

@router.callback_query(F.data.startswith("set_"))
async def set_option_value(callback: CallbackQuery):
    parts = callback.data.split("_")
    category = parts[1]
    value = "_".join(parts[2:])

    key_map = {"border": "border", "bg": "background", "corner": "corner", "spacing": "spacing", "format": "format", "color": "border_color"}
    target_key = "border_color" if category == "color" else key_map.get(category, category)

    await session_manager.update_settings(callback.from_user.id, target_key, value)
    await callback.answer(f"Updated {target_key.replace('_', ' ')} to {value}")

    session = await session_manager.get_or_create(callback.from_user.id)
    await callback.message.edit_text(
        f"✅ Updated <b>{target_key.replace('_', ' ').capitalize()}</b> to <b>{value}</b>",
        parse_mode="HTML",
        reply_markup=get_options_keyboard(category if category != "color" else "border_color", value)
    )

@router.callback_query(F.data == "flow_summary")
async def show_summary_callback(callback: CallbackQuery):
    session = await session_manager.get_or_create(callback.from_user.id)
    summary_text = (
        "✨ <b>Collage Summary</b>\n\n"
        f"📸 <b>Photos:</b> {len(session.get('photos', []))}\n"
        f"🎨 <b>Template:</b> {session.get('template')}\n"
        f"📐 <b>Format:</b> {session.get('format')}\n"
        f"🔲 <b>Border:</b> {session.get('border')} ({session.get('border_color')})\n"
        f"📐 <b>Corners:</b> {session.get('corner')}\n"
        f"↔️ <b>Spacing:</b> {session.get('spacing')}\n"
        f"🖼 <b>Background:</b> {session.get('background')}\n"
        f"📝 <b>Caption:</b> {session.get('caption') or 'None'}\n"
    )
    await callback.message.edit_text(summary_text, parse_mode="HTML", reply_markup=get_preview_keyboard())
    await callback.answer()

@router.callback_query(F.data == "action_render_preview")
async def render_preview_callback(callback: CallbackQuery):
    await callback.answer("⏳ Generating fast preview...")
    session = await session_manager.get_or_create(callback.from_user.id)
    
    try:
        preview_buf = CollageEngine.generate(session, is_preview=True)
        input_file = BufferedInputFile(preview_buf.getvalue(), filename="preview.jpg")
        await callback.message.answer_photo(
            photo=input_file,
            caption="👀 <i>Fast Low-Res Preview</i>",
            parse_mode="HTML",
            reply_markup=get_preview_keyboard()
        )
    except Exception as e:
        await callback.message.answer(f"❌ Failed to build preview: {str(e)}")

@router.callback_query(F.data == "flow_generate")
async def generate_final_collage(callback: CallbackQuery):
    user_id = callback.from_user.id
    session = await session_manager.get_or_create(user_id)

    if len(session.get("photos", [])) < MIN_PHOTOS:
        await callback.answer(f"Please upload at least {MIN_PHOTOS} photos.", show_alert=True)
        return

    status_msg = await callback.message.edit_text("⏳ <i>Preparing your photos...</i>", parse_mode="HTML")
    await callback.answer()

    try:
        await status_msg.edit_text("🎨 <i>Applying layout template...</i>", parse_mode="HTML")
        await status_msg.edit_text("✨ <i>Creating high-res collage...</i>", parse_mode="HTML")
        
        final_image_io = CollageEngine.generate(session, is_preview=False)
        await status_msg.edit_text("📤 <i>Sending finish image...</i>", parse_mode="HTML")

        file = BufferedInputFile(final_image_io.getvalue(), filename="collage.jpg")
        await callback.message.answer_photo(
            photo=file,
            caption="✨ <b>Your high-resolution collage is ready!</b>",
            parse_mode="HTML",
            reply_markup=get_finished_keyboard()
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ Error generating collage: {str(e)}")
