import io
from aiogram import Bot
from config import MAX_FILE_SIZE_BYTES

async def download_telegram_file(bot: Bot, file_id: str) -> bytes:
    file_info = await bot.get_file(file_id)
    if file_info.file_size and file_info.file_size > MAX_FILE_SIZE_BYTES:
        raise ValueError("File size exceeds 20MB limit.")

    file_bytes = io.BytesIO()
    await bot.download_file(file_info.file_path, destination=file_bytes)
    return file_bytes.getvalue()
