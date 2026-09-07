from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import CANVAS_SIZES, BORDER_WIDTHS, BORDER_COLORS, CORNER_RADII, SPACING_SIZES, BACKGROUND_COLORS

def get_upload_keyboard(photo_count: int) -> InlineKeyboardMarkup:
    buttons = []
    if photo_count >= 2:
        buttons.append([InlineKeyboardButton(text="✅ Continue", callback_data="flow_continue")])
        buttons.append([
            InlineKeyboardButton(text="↕️ Arrange Photos", callback_data="flow_arrange"),
            InlineKeyboardButton(text="🎨 Choose Template", callback_data="flow_templates")
        ])
    buttons.append([
        InlineKeyboardButton(text="🗑 Clear", callback_data="action_clear"),
        InlineKeyboardButton(text="❌ Cancel", callback_data="action_cancel")
    ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_arrange_keyboard(photo_count: int, current_idx: int) -> InlineKeyboardMarkup:
    nav_row = []
    if current_idx > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️ Move Left", callback_data=f"arr_left_{current_idx}"))
    if current_idx < photo_count - 1:
        nav_row.append(InlineKeyboardButton(text="➡️ Move Right", callback_data=f"arr_right_{current_idx}"))

    return InlineKeyboardMarkup(
        inline_keyboard=[
            nav_row,
            [InlineKeyboardButton(text="🗑 Remove Photo", callback_data=f"arr_del_{current_idx}")],
            [
                InlineKeyboardButton(text="✅ Done Arranging", callback_data="flow_upload_menu"),
                InlineKeyboardButton(text="🗑 Clear All", callback_data="action_clear")
            ]
        ]
    )

def get_customize_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📐 Canvas Format", callback_data="opt_format")],
            [
                InlineKeyboardButton(text="🔲 Border Style", callback_data="opt_border"),
                InlineKeyboardButton(text="🎨 Border Color", callback_data="opt_border_color")
            ],
            [
                InlineKeyboardButton(text="📐 Corner Style", callback_data="opt_corner"),
                InlineKeyboardButton(text="↔️ Photo Spacing", callback_data="opt_spacing")
            ],
            [
                InlineKeyboardButton(text="🖼 Background", callback_data="opt_bg"),
                InlineKeyboardButton(text="📝 Add Caption", callback_data="opt_caption")
            ],
            [
                InlineKeyboardButton(text="👀 Preview Summary", callback_data="flow_summary"),
                InlineKeyboardButton(text="✨ Generate Collage", callback_data="flow_generate")
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="action_cancel")]
        ]
    )

def get_options_keyboard(category: str, current_value: str) -> InlineKeyboardMarkup:
    options_map = {
        "format": list(CANVAS_SIZES.keys()),
        "border": list(BORDER_WIDTHS.keys()),
        "border_color": list(BORDER_COLORS.keys()),
        "corner": list(CORNER_RADII.keys()),
        "spacing": list(SPACING_SIZES.keys()),
        "bg": list(BACKGROUND_COLORS.keys()),
    }
    
    opts = options_map.get(category, [])
    buttons = []
    for opt in opts:
        label = f"✓ {opt}" if opt == current_value else opt
        buttons.append([InlineKeyboardButton(text=label, callback_data=f"set_{category}_{opt}")])

    buttons.append([InlineKeyboardButton(text="🔙 Back to Customization", callback_data="flow_customize")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_preview_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👀 Full Preview", callback_data="action_render_preview"),
                InlineKeyboardButton(text="✨ Generate Final", callback_data="flow_generate")
            ],
            [
                InlineKeyboardButton(text="✏️ Customize", callback_data="flow_customize"),
                InlineKeyboardButton(text="🎨 Change Template", callback_data="flow_templates")
            ],
            [InlineKeyboardButton(text="❌ Cancel", callback_data="action_cancel")]
        ]
    )

def get_finished_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔄 Create Another", callback_data="cmd_create"),
                InlineKeyboardButton(text="✏️ Edit Current", callback_data="flow_customize")
            ],
            [InlineKeyboardButton(text="🗑 Clear Session", callback_data="action_clear")]
        ]
    )
