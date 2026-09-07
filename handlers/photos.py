from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from config import MAX_PHOTOS, MIN_PHOTOS
from services.session_manager import session_manager
from utils.helpers import download_telegram_file
from keyboards.collage import get_upload_keyboard, get_arrange_keyboard
from PIL import Image
import io

router = Router()

class PhotoUploadState(StatesGroup):
    waiting_for_photos = State()
    waiting_for_caption = State()

@router.message(F.photo)
@router.message(F.document.mime_type.startswith("image/"))
async def handle_photo_upload(message: Message, bot):
    user_id = message.from_user.id
    session = await session_manager.get_or_create(user_id)
    current_count = len(session.get("photos", []))

    if current_count >= MAX_PHOTOS:
        await message.answer(f"⚠️ You have reached the maximum limit of {MAX_PHOTOS} photos.")
        return

    file_id = message.photo[-1].file_id if message.photo else message.document.file_id

    try:
        file_bytes = await download_telegram_file(bot, file_id)
        # Verify valid image stream
        with Image.open(io.BytesIO(file_bytes)) as img:
            img.verify()
        
        new_count = await session_manager.add_photo(user_id, file_bytes)
        await message.answer(
            f"📸 <b>Photo added:</b> {new_count}/{MAX_PHOTOS}\n"
            f"{'Send more photos or click Continue below when ready.' if new_count >= MIN_PHOTOS else f'Please upload at least {MIN_PHOTOS - new_count} more photo(s).'}",
            parse_mode="HTML",
            reply_markup=get_upload_keyboard(new_count)
        )
    except Exception as e:
        await message.answer("❌ Invalid or corrupted image file. Please try uploading another standard photo.")

@router.callback_query(F.data == "flow_upload_menu")
async def show_upload_menu_callback(callback: CallbackQuery):
    session = await session_manager.get_or_create(callback.from_user.id)
    count = len(session.get("photos", []))
    await callback.message.edit_text(
        f"📸 <b>Photos added:</b> {count}/{MAX_PHOTOS}\n\nUpload more photos or choose an option below:",
        parse_mode="HTML",
        reply_markup=get_upload_keyboard(count)
    )
    await callback.answer()

@router.callback_query(F.data == "flow_arrange")
async def arrange_photos_callback(callback: CallbackQuery):
    session = await session_manager.get_or_create(callback.from_user.id)
    photos = session.get("photos", [])
    if not photos:
        await callback.answer("No photos to arrange.", show_alert=True)
        return

    await show_arrange_card(callback, photos, 0)

async def show_arrange_card(callback: CallbackQuery, photos: list, index: int):
    total = len(photos)
    text = f"<b>↕️ Photo arrangement ({index + 1}/{total}):</b>\nUse arrows to change position or remove items."
    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        reply_markup=get_arrange_keyboard(total, index)
    )

@router.callback_query(F.data.startswith("arr_left_"))
async def arr_left_callback(callback: CallbackQuery):
    idx = int(callback.data.replace("arr_left_", ""))
    session = await session_manager.get_or_create(callback.from_user.id)
    photos = session.get("photos", [])
    if idx > 0:
        photos[idx], photos[idx - 1] = photos[idx - 1], photos[idx]
        await session_manager.update_settings(callback.from_user.id, "photos", photos)
        await show_arrange_card(callback, photos, idx - 1)
    await callback.answer()

@router.callback_query(F.data.startswith("arr_right_"))
async def arr_right_callback(callback: CallbackQuery):
    idx = int(callback.data.replace("arr_right_", ""))
    session = await session_manager.get_or_create(callback.from_user.id)
    photos = session.get("photos", [])
    if idx < len(photos) - 1:
        photos[idx], photos[idx + 1] = photos[idx + 1], photos[idx]
        await session_manager.update_settings(callback.from_user.id, "photos", photos)
        await show_arrange_card(callback, photos, idx + 1)
    await callback.answer()

@router.callback_query(F.data.startswith("arr_del_"))
async def arr_del_callback(callback: CallbackQuery):
    idx = int(callback.data.replace("arr_del_", ""))
    session = await session_manager.get_or_create(callback.from_user.id)
    photos = session.get("photos", [])
    if 0 <= idx < len(photos):
        photos.pop(idx)
        await session_manager.update_settings(callback.from_user.id, "photos", photos)

    if not photos:
        await callback.message.edit_text("All photos removed. Send new photos to begin.", parse_mode="HTML")
    else:
        new_idx = min(idx, len(photos) - 1)
        await show_arrange_card(callback, photos, new_idx)
    await callback.answer("Photo removed.")
