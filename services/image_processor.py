import io
from PIL import Image, ImageDraw, ImageOps, ImageFilter, ImageFont

def resize_and_crop(img: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    """Intelligently resize and center-crop image to target dimensions."""
    target_width, target_height = target_size
    aspect_target = target_width / target_height
    aspect_img = img.width / img.height

    if aspect_img > aspect_target:
        # Image is wider: fit height, crop sides
        new_height = target_height
        new_width = int(new_height * aspect_img)
    else:
        # Image is taller: fit width, crop top/bottom
        new_width = target_width
        new_height = int(new_width / aspect_img)

    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    return resized.crop((left, top, left + target_width, top + target_height))


def apply_rounded_corners(img: Image.Image, radius: int) -> Image.Image:
    """Apply smooth rounded corners using antialiased alpha masking."""
    if radius <= 0:
        return img.convert("RGBA")

    mask = Image.new("L", (img.width * 4, img.height * 4), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, mask.width, mask.height), radius=radius * 4, fill=255)
    mask = mask.resize(img.size, Image.Resampling.LANCZOS)

    output = img.convert("RGBA")
    output.putalpha(mask)
    return output


def add_border_to_image(img: Image.Image, border_width: int, border_color: tuple[int, int, int]) -> Image.Image:
    """Add colored border around individual photo."""
    if border_width <= 0:
        return img

    w, h = img.size
    bordered_w = w + border_width * 2
    bordered_h = h + border_width * 2

    canvas = Image.new("RGBA", (bordered_w, bordered_h), border_color + (255,))
    canvas.paste(img, (border_width, border_width), img if img.mode == "RGBA" else None)
    return canvas


def draw_caption(
    canvas: Image.Image,
    text: str,
    position: str = "Bottom",
    bg_color: tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """Draw caption text with adaptive font scaling."""
    if not text.strip():
        return canvas

    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size

    # Luminance formula for high contrast text color calculation
    luminance = (0.299 * bg_color[0] + 0.587 * bg_color[1] + 0.114 * bg_color[2]) / 255
    text_color = (0, 0, 0) if luminance > 0.5 else (255, 255, 255)

    max_font_size = max(16, int(h * 0.05))
    font_size = max_font_size

    try:
        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()

    # Dynamic text downsizing
    while font_size > 10:
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        if text_w <= w * 0.9:
            break
        font_size -= 2
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", font_size)
        except IOError:
            break

    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = (w - text_w) // 2
    padding = int(h * 0.02)
    y = padding if position == "Top" else (h - text_h - padding * 2)

    draw.text((x, y), text, fill=text_color, font=font)
    return canvas
