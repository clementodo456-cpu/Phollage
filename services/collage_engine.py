import io
import math
from typing import List, Tuple
from PIL import Image, ImageDraw
from config import (
    CANVAS_SIZES, BORDER_WIDTHS, BORDER_COLORS,
    CORNER_RADII, SPACING_SIZES, BACKGROUND_COLORS, PREVIEW_MAX_DIM
)
from services.image_processor import (
    resize_and_crop, apply_rounded_corners, add_border_to_image, draw_caption
)

class CollageEngine:

    @staticmethod
    def _create_base_canvas(
        canvas_size: Tuple[int, int],
        bg_name: str,
        caption: str,
        caption_pos: str
    ) -> Tuple[Image.Image, Tuple[int, int, int, int]]:
        bg_rgb = BACKGROUND_COLORS.get(bg_name, (255, 255, 255))
        canvas = Image.new("RGBA", canvas_size, bg_rgb + (255,))
        w, h = canvas_size

        top_offset = 0
        bottom_offset = 0

        if caption.strip():
            reserved_height = int(h * 0.08)
            if caption_pos == "Top":
                top_offset = reserved_height
            else:
                bottom_offset = reserved_height

        usable_box = (0, top_offset, w, h - bottom_offset)
        return canvas, usable_box

    @classmethod
    def generate(cls, session: dict, is_preview: bool = False) -> io.BytesIO:
        photos_bytes: List[bytes] = session.get("photos", [])
        if not photos_bytes:
            raise ValueError("No photos provided for collage generation.")

        images = [Image.open(io.BytesIO(pb)).convert("RGBA") for pb in photos_bytes]
        
        target_size = CANVAS_SIZES.get(session.get("format"), (1200, 1200))
        if is_preview:
            ratio = min(PREVIEW_MAX_DIM / target_size[0], PREVIEW_MAX_DIM / target_size[1])
            target_size = (int(target_size[0] * ratio), int(target_size[1] * ratio))

        template = session.get("template", "Classic Grid")
        bg_name = session.get("background", "White")
        caption = session.get("caption", "")
        caption_pos = session.get("caption_position", "Bottom")

        canvas, usable_area = cls._create_base_canvas(target_size, bg_name, caption, caption_pos)
        
        # Calculate photos within bounding bounds
        rendered_layout = cls._render_template_layout(template, images, usable_area, session, is_preview)
        canvas.alpha_composite(rendered_layout)

        if caption.strip():
            bg_rgb = BACKGROUND_COLORS.get(bg_name, (255, 255, 255))
            canvas = draw_caption(canvas, caption, caption_pos, bg_rgb)

        final_rgb = Image.new("RGB", canvas.size, BACKGROUND_COLORS.get(bg_name, (255, 255, 255)))
        final_rgb.paste(canvas, mask=canvas.split()[3])

        output = io.BytesIO()
        final_rgb.save(output, format="JPEG", quality=85 if is_preview else 95)
        output.seek(0)
        return output

    @classmethod
    def _render_template_layout(
        cls,
        template: str,
        images: List[Image.Image],
        bounds: Tuple[int, int, int, int],
        session: dict,
        is_preview: bool
    ) -> Image.Image:
        scale = 0.5 if is_preview else 1.0
        spacing = int(SPACING_SIZES.get(session.get("spacing", "Medium"), 20) * scale)
        border_w = int(BORDER_WIDTHS.get(session.get("border", "Thin"), 10) * scale)
        border_color = BORDER_COLORS.get(session.get("border_color", "White"), (255, 255, 255))
        corner_r = int(CORNER_RADII.get(session.get("corner", "Slightly Rounded"), 15) * scale)

        start_x, start_y, end_x, end_y = bounds
        usable_w = end_x - start_x
        usable_h = end_y - start_y

        layout_layer = Image.new("RGBA", (start_x + usable_w, start_y + usable_h), (0, 0, 0, 0))
        num_photos = len(images)

        boxes = cls._compute_boxes(template, num_photos, start_x, start_y, usable_w, usable_h, spacing)

        for idx, box in enumerate(boxes):
            if idx >= len(images):
                break
            bx, by, bw, bh = box
            if bw <= 0 or bh <= 0:
                continue

            cropped = resize_and_crop(images[idx], (bw, bh))
            if border_w > 0:
                cropped = resize_and_crop(images[idx], (max(1, bw - border_w * 2), max(1, bh - border_w * 2)))
                cropped = add_border_to_image(cropped, border_w, border_color)
                cropped = resize_and_crop(cropped, (bw, bh))

            if corner_r > 0:
                cropped = apply_rounded_corners(cropped, corner_r)

            layout_layer.paste(cropped, (bx, by), cropped if cropped.mode == "RGBA" else None)

        return layout_layer

    @staticmethod
    def _compute_boxes(
        template: str, num_photos: int, x0: int, y0: int, w: int, h: int, spacing: int
    ) -> List[Tuple[int, int, int, int]]:
        boxes = []

        if template in ["Classic Grid", "2x2 Grid", "3x3 Grid"]:
            if template == "2x2 Grid":
                cols, rows = 2, 2
            elif template == "3x3 Grid":
                cols, rows = 3, 3
            else:
                cols = math.ceil(math.sqrt(num_photos))
                rows = math.ceil(num_photos / cols)

            item_w = (w - (cols + 1) * spacing) // cols
            item_h = (h - (rows + 1) * spacing) // rows

            for i in range(num_photos):
                r = i // cols
                c = i % cols
                bx = x0 + spacing + c * (item_w + spacing)
                by = y0 + spacing + r * (item_h + spacing)
                boxes.append((bx, by, item_w, item_h))

        elif template == "Film Strip":
            is_vertical = h >= w
            if is_vertical:
                item_w = w - (spacing * 2)
                item_h = (h - (num_photos + 1) * spacing) // num_photos
                for i in range(num_photos):
                    bx = x0 + spacing
                    by = y0 + spacing + i * (item_h + spacing)
                    boxes.append((bx, by, item_w, item_h))
            else:
                item_w = (w - (num_photos + 1) * spacing) // num_photos
                item_h = h - (spacing * 2)
                for i in range(num_photos):
                    bx = x0 + spacing + i * (item_w + spacing)
                    by = y0 + spacing
                    boxes.append((bx, by, item_w, item_h))

        elif template == "Magazine":
            if num_photos == 1:
                boxes.append((x0 + spacing, y0 + spacing, w - 2 * spacing, h - 2 * spacing))
            else:
                top_h = int((h - 3 * spacing) * 0.6)
                bottom_h = (h - 3 * spacing) - top_h
                boxes.append((x0 + spacing, y0 + spacing, w - 2 * spacing, top_h))

                rem_photos = num_photos - 1
                sub_w = (w - (rem_photos + 1) * spacing) // rem_photos
                for i in range(rem_photos):
                    bx = x0 + spacing + i * (sub_w + spacing)
                    by = y0 + 2 * spacing + top_h
                    boxes.append((bx, by, sub_w, bottom_h))

        elif template in ["Masonry", "Polaroid", "Story"]:
            cols = 2 if num_photos <= 4 else 3
            rows = math.ceil(num_photos / cols)
            item_w = (w - (cols + 1) * spacing) // cols
            item_h = (h - (rows + 1) * spacing) // rows

            for i in range(num_photos):
                r = i // cols
                c = i % cols
                bx = x0 + spacing + c * (item_w + spacing)
                by = y0 + spacing + r * (item_h + spacing)
                boxes.append((bx, by, item_w, item_h))

        return boxes
