from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TEMPLATES

def get_templates_keyboard(current_template: str = "") -> InlineKeyboardMarkup:
    buttons = []
    for tpl in TEMPLATES:
        label = f"⭐ {tpl}" if tpl == current_template else tpl
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"set_template_{tpl}")])
    
    buttons.append([InlineKeyboardButton(text="🔙 Back to Customization", callback_data="flow_customize")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
