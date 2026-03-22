"""
Generate print-ready front + back labels for all Real Health Kombucha flavours.
Output: output/labels/<flavour>_front.png and _back.png at 896×1133 / 896×956 px (300 DPI, 3 mm bleed).
"""
import os
from PIL import Image, ImageDraw, ImageFont

from src.label_utils import (
    load_font, draw_spaced_text, spaced_text_width,
    draw_diamond_rule, draw_sunburst, draw_island, paste_watercolor,
)

def load_script(size: int) -> ImageFont.FreeTypeFont:
    """Load Brush Script with Bradley Hand as fallback."""
    for path in [
        "/System/Library/Fonts/Supplemental/Brush Script.ttf",
        "/System/Library/Fonts/Supplemental/Bradley Hand Bold.ttf",
        "/System/Library/Fonts/Supplemental/Apple Chancery.ttf",
    ]:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return load_font(size, italic=True)

# ---------------------------------------------------------------------------
# Canvas constants
# ---------------------------------------------------------------------------
BLEED          = 35          # px — 3 mm at 300 DPI
FRONT_W        = 896
FRONT_H        = 1133
BACK_W         = 896
BACK_H         = 956
SAFE           = BLEED       # live area starts SAFE px from each edge
CREAM          = "#FFFDF8"
BROWN          = "#3D2B1F"
AMBER          = "#8B4513"

# ---------------------------------------------------------------------------
# Flavour configuration
# ---------------------------------------------------------------------------
BASE_INGREDIENTS = (
    "Filtered structured water, fermented green tea "
    "(Camellia sinensis), raw cane sugar*, "
    "kombucha culture (SCOBY)"
)
FOOTNOTE = "*Partially consumed during fermentation."

FLAVOURS = {
    "ginger": {
        "display_name": "Ginger",
        "colors": {"light": "#FDFAE8", "mid": "#EAD878", "dark": "#C4A030", "band": "#C4A030"},
        "watercolor": "assets/water-colors/01-ginger.png",
        "addition": "ginger (Zingiber officinale)",
    },
    "wild_orange": {
        "display_name": "Wild Orange",
        "colors": {"light": "#FFF3D0", "mid": "#FFAA40", "dark": "#FF7000", "band": "#FF7000"},
        "watercolor": "assets/water-colors/02-wild-orange.png",
        "addition": "wild orange juice (Citrus sinensis)",
    },
    "green_mandarine": {
        "display_name": "Green Mandarine",
        "colors": {"light": "#E8F8D0", "mid": "#8CC840", "dark": "#F0882A", "band": "#6A9010"},
        "watercolor": "assets/water-colors/03-green-mandarine.png",
        "addition": "green mandarine juice (Citrus reticulata)",
    },
    "turmeric_lemon": {
        "display_name": "Turmeric + Lemon",
        "colors": {"light": "#FFFBA0", "mid": "#F5E020", "dark": "#C8A000", "band": "#C8A000"},
        "watercolor": "assets/water-colors/04-lemon-turmeric.png",
        "addition": "lemon juice (Citrus limon), turmeric (Curcuma longa)",
    },
    "metabolic_boost": {
        "display_name": "Metabolic Boost",
        "colors": {"light": "#FFE8C0", "mid": "#FF4500", "dark": "#8B0000", "band": "#CC2000"},
        "watercolor": "assets/water-colors/05-meta-boost.png",
        "addition": (
            "grapefruit juice (Citrus paradisi), lemon juice (Citrus limon), "
            "peppermint (Mentha piperita), ginger (Zingiber officinale), "
            "cinnamon (Cinnamomum verum)"
        ),
    },
    "lime": {
        "display_name": "Lime",
        "colors": {"light": "#F4FAC0", "mid": "#A8D428", "dark": "#5A8A10", "band": "#5A8A10"},
        "watercolor": "assets/water-colors/06-lime.png",
        "addition": "lime juice (Citrus aurantifolia)",
    },
}

HEXAGONAL_WATER_IMG = "assets/water-colors/07-hexagonal-water.png"
LOGO_PATH           = "assets/design-logos/logo_transparent_highres.png"
# Pre-measured content bounding box of the transparent logo (non-transparent pixels)
LOGO_CONTENT_BBOX   = (274, 326, 1727, 1266)   # 1453 × 940 px of actual content
OUTPUT_DIR = "output/labels"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _wrap_text(text: str, font, max_width: int) -> list:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip()
        bb = font.getbbox(test)
        if bb[2] - bb[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


# ---------------------------------------------------------------------------
# Front label
# ---------------------------------------------------------------------------
def build_front_label(key: str, cfg: dict) -> Image.Image:
    img  = Image.new("RGB", (FRONT_W, FRONT_H), CREAM)
    draw = ImageDraw.Draw(img)
    c    = cfg["colors"]
    s    = SAFE

    f_kombucha = load_font(120, bold=True)
    f_flavour  = load_font(70, bold=True)
    f_tagline  = load_script(36)
    f_qty      = load_font(26)

    cx = FRONT_W // 2

    # --- 1. Flavour colour stripe — top ---
    draw.rectangle([0, 0, FRONT_W, s - 1], fill=c["mid"])

    # --- 2. Logo image — scale to 55% of live width to leave room for KOMBUCHA ---
    logo         = Image.open(LOGO_PATH).convert("RGBA")
    logo_content = logo.crop(LOGO_CONTENT_BBOX)           # 1453 × 940 px
    target_w     = int((FRONT_W - 2 * s) * 0.30)         # ~248 px
    target_h     = int(target_w * logo_content.height / logo_content.width)
    logo_scaled  = logo_content.resize((target_w, target_h), Image.LANCZOS)
    logo_x       = (FRONT_W - target_w) // 2
    logo_y       = s + 40
    img.paste(logo_scaled, (logo_x, logo_y), mask=logo_scaled.split()[3])
    logo_bottom  = logo_y + target_h

    # --- 3. KOMBUCHA text — centred in the gap between logo and watercolor ---
    band_height  = 95 + 38 + 20
    stripe_h     = 8
    illus_bottom = FRONT_H - s - stripe_h - band_height
    gap_height   = 170                              # fixed space reserved between logo and watercolor
    illus_top    = logo_bottom + gap_height

    kom_text = "KOMBUCHA"
    kom_bb   = f_kombucha.getbbox("A")
    kom_h    = kom_bb[3] - kom_bb[1]
    kom_w    = spaced_text_width(kom_text, f_kombucha, spacing=8)
    kom_x    = cx - kom_w // 2
    # Subtract kom_bb[1] so the visual top of the glyph (not the draw origin) is centred
    kom_y    = logo_bottom + (gap_height - kom_h) // 2 - kom_bb[1]
    draw_spaced_text(draw, kom_x, kom_y, kom_text, f_kombucha, AMBER, spacing=8)

    # --- 4. Watercolor illustration ---
    paste_watercolor(img, cfg["watercolor"],
                     (s + 10, illus_top, FRONT_W - s - 10, illus_bottom))

    # --- 5. Flavour band ---
    band_y   = illus_bottom
    band_bot = FRONT_H - s - stripe_h
    draw.rectangle([0, band_y, FRONT_W, band_bot], fill=c["band"])

    fn_text = cfg["display_name"].upper()
    fn_w    = spaced_text_width(fn_text, f_flavour, spacing=5)
    fn_x    = cx - fn_w // 2
    fn_y    = band_y + 12
    draw_spaced_text(draw, fn_x, fn_y, fn_text, f_flavour, "#FFFFFF", spacing=5)

    tg_text = "Handcrafted in Madeira"
    tg_bb   = f_tagline.getbbox(tg_text)
    tg_x    = cx - (tg_bb[2] - tg_bb[0]) // 2
    tg_y    = fn_y + 74
    draw.text((tg_x, tg_y), tg_text, font=f_tagline, fill="#FFEEBB")

    # --- 6. Bottom stripe ---
    draw.rectangle([0, band_bot, FRONT_W, FRONT_H], fill=c["mid"])

    # --- 7. Net quantity ---
    qty_text = "250 ml e"
    qty_bb   = f_qty.getbbox(qty_text)
    qty_x    = FRONT_W - s - (qty_bb[2] - qty_bb[0]) - 24
    qty_y    = FRONT_H - s - stripe_h - (qty_bb[3] - qty_bb[1]) - 16
    draw.text((qty_x, qty_y), qty_text, font=f_qty, fill=BROWN)

    return img


# ---------------------------------------------------------------------------
# Back label
# ---------------------------------------------------------------------------
def build_back_label(key: str, cfg: dict) -> Image.Image:
    img  = Image.new("RGB", (BACK_W, BACK_H), CREAM)
    draw = ImageDraw.Draw(img)
    c    = cfg["colors"]
    s    = SAFE

    # --- Fonts — sized to fill the 886px live area ---
    f_title  = load_font(38, bold=True)
    f_body   = load_font(26)
    f_footer = load_font(22)
    BODY_LINE  = 36   # line height for body text
    FOOT_LINE  = 30   # line height for footer text

    text_x = s + 12
    text_w = BACK_W - 2 * s - 24

    # --- 1. Top stripe ---
    draw.rectangle([0, 0, BACK_W, s - 1], fill=c["mid"])

    y = s + 18

    # --- 2. Structured Water section ---
    icon_size = 56
    try:
        icon = Image.open(HEXAGONAL_WATER_IMG).convert("RGB")
        icon = icon.resize((icon_size, icon_size), Image.LANCZOS)
        img.paste(icon, (text_x, y))
    except Exception:
        pass
    draw.text((text_x + icon_size + 14, y + 8), "STRUCTURED WATER",
              font=f_title, fill=BROWN)
    y += icon_size + 14

    water_body = (
        "Water filtered through activated carbon and structured "
        "using the UMH Pure Gold energiser — a technical conditioning "
        "process that restores the water\u2019s natural hexagonal molecular "
        "arrangement."
    )
    for line in _wrap_text(water_body, f_body, text_w):
        draw.text((text_x, y), line, font=f_body, fill="#444444")
        y += BODY_LINE
    y += 18

    draw.line([(s, y), (BACK_W - s, y)], fill="#D9BC8A", width=2)
    y += 18

    # --- 3. Ingredients section ---
    draw.text((text_x, y), "INGREDIENTS", font=f_title, fill=BROWN)
    y += 50

    full_ingredients = (
        f"{BASE_INGREDIENTS}, {cfg['addition']}. {FOOTNOTE}"
    )
    for line in _wrap_text(full_ingredients, f_body, text_w):
        draw.text((text_x, y), line, font=f_body, fill="#444444")
        y += BODY_LINE
    y += 18

    draw.line([(s, y), (BACK_W - s, y)], fill="#D9BC8A", width=2)
    y += 18

    # --- 4. Nutritional highlights ---
    draw.text((text_x, y), "PER 250 ml", font=f_title, fill=BROWN)
    y += 50

    nutrition_lines = [
        "Energy: ~20 kcal / 84 kJ",
        "Sugars: ~4 g  (naturally occurring, partially consumed)",
        "Live probiotic cultures: present",
        "Alcohol: <0.5% vol  (naturally fermented)",
    ]
    for line in nutrition_lines:
        draw.text((text_x, y), line, font=f_body, fill="#444444")
        y += BODY_LINE
    y += 18

    draw.line([(s, y), (BACK_W - s, y)], fill="#D9BC8A", width=2)
    y += 18

    # --- 5. Legal footer ---
    footer_lines = [
        "Store refrigerated after opening. Shake gently before serving.",
        "Best before: ............  (DD/MM/YYYY)",
        "Contains live cultures  \u00b7  Naturally fermented <0.5% vol",
        "Real Health Kombucha  \u00b7  Caminho de Jangao 154",
        "9360-523 Ponta do Sol  \u00b7  Madeira, Portugal",
    ]
    for line in footer_lines:
        draw.text((text_x, y), line, font=f_footer, fill="#888888")
        y += FOOT_LINE

    # --- 6. Bottom stripe ---
    draw.rectangle([0, BACK_H - s, BACK_W, BACK_H], fill=c["mid"])

    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    for key, cfg in FLAVOURS.items():
        print(f"Generating {cfg['display_name']}...")
        front = build_front_label(key, cfg)
        front.save(os.path.join(OUTPUT_DIR, f"{key}_front.png"))
        back = build_back_label(key, cfg)
        back.save(os.path.join(OUTPUT_DIR, f"{key}_back.png"))
        print(f"  ✓ {key}_front.png  {key}_back.png")


if __name__ == "__main__":
    main()
