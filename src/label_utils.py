import math
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_FONT_PATHS = {
    "regular": [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
    ],
    "bold": [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ],
    "italic": [
        "/System/Library/Fonts/Supplemental/Georgia Italic.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ],
}


def load_font(size: int, bold: bool = False, italic: bool = False) -> ImageFont.FreeTypeFont:
    """Load Georgia (or fallback) at given pixel size."""
    style = "bold" if bold else ("italic" if italic else "regular")
    for path in _FONT_PATHS[style]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def spaced_text_width(text: str, font: ImageFont.FreeTypeFont, spacing: int) -> int:
    total = 0
    for ch in text:
        bb = font.getbbox(ch)
        total += (bb[2] - bb[0]) + spacing
    return max(0, total - spacing)


def draw_spaced_text(draw: ImageDraw.ImageDraw, x: int, y: int,
                     text: str, font: ImageFont.FreeTypeFont,
                     color: str, spacing: int) -> None:
    for ch in text:
        draw.text((x, y), ch, font=font, fill=color)
        bb = font.getbbox(ch)
        x += (bb[2] - bb[0]) + spacing


def draw_diamond_rule(draw: ImageDraw.ImageDraw, cx: int, y: int,
                      width: int, color: str, diamond_size: int = 5) -> None:
    x0, x1 = cx - width // 2, cx + width // 2
    draw.line([(x0, y), (x1, y)], fill=color, width=1)
    ds = diamond_size
    for dx in [x0, x1]:
        draw.polygon([(dx, y - ds), (dx + ds, y), (dx, y + ds), (dx - ds, y)], fill=color)


def _sunburst_ray_polygon(cx, cy, angle_rad, r_inner, r_outer, half_ang):
    a0, a1 = angle_rad - half_ang, angle_rad + half_ang
    return [
        (cx + r_inner * math.cos(a0), cy + r_inner * math.sin(a0)),
        (cx + r_outer * math.cos(angle_rad), cy + r_outer * math.sin(angle_rad)),
        (cx + r_inner * math.cos(a1), cy + r_inner * math.sin(a1)),
    ]


def draw_sunburst(draw: ImageDraw.ImageDraw, cx: int, cy: int,
                  r_outer_long: int, r_outer_short: int, r_inner: int,
                  ray_count: int, color: str, bg: str,
                  ray_half_ang: float = math.radians(2.8)) -> None:
    for i in range(ray_count):
        angle = math.radians(i * 360 / ray_count) - math.pi / 2
        r_tip = r_outer_long if (i % 2 == 0) else r_outer_short
        poly = _sunburst_ray_polygon(cx, cy, angle, r_inner, r_tip, ray_half_ang)
        draw.polygon(poly, fill=color)
    draw.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=bg)


def draw_island(draw: ImageDraw.ImageDraw, cx: int, cy: int,
                w: int = 90, h: int = 34,
                tilt_deg: float = 4, color: str = "#3D2B1F") -> None:
    tilt = math.radians(tilt_deg)
    pts = []
    for deg in range(0, 361, 6):
        t = math.radians(deg)
        bump = 1.0 + 0.08 * math.sin(3 * t) + 0.05 * math.cos(5 * t)
        rx = (w / 2) * math.cos(t) * bump
        ry = (h / 2) * math.sin(t) * bump
        x = cx + rx * math.cos(tilt) - ry * math.sin(tilt)
        y = cy + rx * math.sin(tilt) + ry * math.cos(tilt)
        pts.append((x, y))
    draw.polygon(pts, fill=color)


def paste_watercolor(label_img: Image.Image, img_path: str,
                     bbox: tuple) -> None:
    """Scale-to-fill + centre-crop watercolor image into bbox."""
    wc = Image.open(img_path).convert("RGB")
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    scale = max(bw / wc.width, bh / wc.height)
    new_w = int(wc.width * scale)
    new_h = int(wc.height * scale)
    wc = wc.resize((new_w, new_h), Image.LANCZOS)
    x0 = (new_w - bw) // 2
    y0 = (new_h - bh) // 2
    wc = wc.crop((x0, y0, x0 + bw, y0 + bh))
    label_img.paste(wc, (bbox[0], bbox[1]))
