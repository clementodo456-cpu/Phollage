from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🖼 Create Collage", callback_data="cmd_create")],
            [
                InlineKeyboardButton(text="🎨 Templates", callback_data="cmd_templates"),
                InlineKeyboardButton(text="📖 How It Works", callback_data="cmd_help")
            ],
            [InlineKeyboardButton(text="ℹ️ About", callback_data="cmd_about")]
        ]
    )

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Cancel", callback_data="action_cancel")]
        ]
    )
