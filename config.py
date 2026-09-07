import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not defined in environment variables.")

MAX_PHOTOS = 20
MIN_PHOTOS = 2
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB max photo size
SESSION_TIMEOUT_SECONDS = 1800  # 30 minutes cleanup

# Standard export canvas size (pixels)
CANVAS_SIZES = {
    "Square (1:1)": (1200, 1200),
    "Portrait (4:5)": (1200, 1500),
    "Story (9:16)": (1080, 1920),
    "Landscape (16:9)": (1920, 1080),
    "Classic (3:2)": (1500, 1000)
}

PREVIEW_MAX_DIM = 600

BORDER_WIDTHS = {
    "None": 0,
    "Thin": 10,
    "Medium": 20,
    "Thick": 35
}

BORDER_COLORS = {
    "White": (255, 255, 255),
    "Black": (0, 0, 0),
    "Gray": (128, 128, 128)
}

BACKGROUND_COLORS = {
    "White": (255, 255, 255),
    "Black": (18, 18, 18),
    "Light Gray": (240, 240, 240),
    "Dark Gray": (40, 40, 40)
}

CORNER_RADII = {
    "Square": 0,
    "Slightly Rounded": 15,
    "Rounded": 30,
    "Very Rounded": 50
}

SPACING_SIZES = {
    "None": 0,
    "Small": 10,
    "Medium": 20,
    "Large": 35
}

TEMPLATES = [
    "Classic Grid",
    "Masonry",
    "Magazine",
    "Film Strip",
    "Polaroid",
    "2x2 Grid",
    "3x3 Grid",
    "Story"
]
