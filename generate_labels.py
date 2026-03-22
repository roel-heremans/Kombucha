"""
Generate print-ready front + back labels for all Real Health Kombucha flavours.
Output: output/labels/<flavour>_front.png and _back.png at 896×1133 / 896×956 px (300 DPI, 3 mm bleed).
"""
import os
from PIL import Image, ImageDraw

from src.label_utils import (
    load_font, draw_spaced_text, spaced_text_width,
    draw_diamond_rule, draw_sunburst, draw_island, paste_watercolor,
)

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

    # --- Fonts ---
    f_real_health = load_font(217, bold=True)
    f_kombucha    = load_font(158, bold=True)
    f_flavour     = load_font(100, bold=True)
    f_tagline     = load_font(58,  italic=True)
    f_qty         = load_font(42)

    # --- 1. Flavour colour stripe — top ---
    draw.rectangle([0, 0, FRONT_W, s - 1], fill=c["mid"])

    # --- 2. Logo zone ---
    logo_top   = s + 10
    sb_cx      = FRONT_W // 2
    sb_cy      = logo_top + 135
    draw_sunburst(draw, sb_cx, sb_cy,
                  r_outer_long=120, r_outer_short=88, r_inner=38,
                  ray_count=30, color=BROWN, bg=CREAM)
    draw_island(draw, sb_cx, sb_cy, w=72, h=28, tilt_deg=4, color=BROWN)

    # Diamond rule above REAL HEALTH
    rule_y1 = sb_cy + 145
    draw_diamond_rule(draw, sb_cx, rule_y1, width=560, color=AMBER)

    # REAL HEALTH
    rh_text  = "REAL HEALTH"
    rh_w     = spaced_text_width(rh_text, f_real_health, spacing=9)
    rh_x     = sb_cx - rh_w // 2
    rh_y     = rule_y1 + 14
    draw_spaced_text(draw, rh_x, rh_y, rh_text, f_real_health, BROWN, spacing=9)
    rh_h     = f_real_health.getbbox("A")[3]

    # Diamond rule below REAL HEALTH
    rule_y2  = rh_y + rh_h + 10
    draw_diamond_rule(draw, sb_cx, rule_y2, width=560, color=AMBER)

    # --- 3. KOMBUCHA ---
    kom_text = "KOMBUCHA"
    kom_w    = spaced_text_width(kom_text, f_kombucha, spacing=8)
    kom_x    = sb_cx - kom_w // 2
    kom_y    = rule_y2 + 14
    draw_spaced_text(draw, kom_x, kom_y, kom_text, f_kombucha, AMBER, spacing=8)
    kom_h    = f_kombucha.getbbox("A")[3]

    # --- 4. Watercolor illustration ---
    illus_top    = kom_y + kom_h + 12
    band_height  = 100 + 40 + 20
    stripe_h     = 8
    illus_bottom = FRONT_H - s - stripe_h - band_height
    paste_watercolor(img, cfg["watercolor"],
                     (s + 10, illus_top, FRONT_W - s - 10, illus_bottom))

    # --- 5. Flavour band ---
    band_y = illus_bottom
    band_bot = FRONT_H - s - stripe_h
    draw.rectangle([0, band_y, FRONT_W, band_bot], fill=c["band"])

    fn_text = cfg["display_name"].upper()
    fn_w    = spaced_text_width(fn_text, f_flavour, spacing=5)
    fn_x    = sb_cx - fn_w // 2
    fn_y    = band_y + 10
    draw_spaced_text(draw, fn_x, fn_y, fn_text, f_flavour, "#FFFFFF", spacing=5)

    tg_text = "Handcrafted in Madeira"
    tg_bb   = f_tagline.getbbox(tg_text)
    tg_w    = tg_bb[2] - tg_bb[0]
    tg_x    = sb_cx - tg_w // 2
    tg_y    = fn_y + 105
    draw.text((tg_x, tg_y), tg_text, font=f_tagline, fill="#FFEEBB")

    # --- 6. Bottom stripe ---
    draw.rectangle([0, band_bot, FRONT_W, FRONT_H], fill=c["mid"])

    # --- 7. Net quantity (bottom-right of live area) ---
    qty_text = "250 ml e"
    qty_bb   = f_qty.getbbox(qty_text)
    qty_x    = FRONT_W - s - (qty_bb[2] - qty_bb[0]) - 8
    qty_y    = FRONT_H - s - stripe_h - (qty_bb[3] - qty_bb[1]) - 4
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

    # --- Fonts ---
    f_title  = load_font(22, bold=True)
    f_body   = load_font(19)
    f_footer = load_font(19)

    live_w = BACK_W - 2 * s
    text_w = live_w - 20

    # --- 1. Top stripe ---
    draw.rectangle([0, 0, BACK_W, s - 1], fill=c["mid"])

    y = s + 10

    # --- 2. Structured Water section ---
    try:
        icon = Image.open(HEXAGONAL_WATER_IMG).convert("RGB")
        icon = icon.resize((40, 40), Image.LANCZOS)
        img.paste(icon, (s + 8, y))
    except Exception:
        pass
    draw.text((s + 56, y + 8), "STRUCTURED WATER",
              font=f_title, fill=BROWN)
    y += 48

    water_body = (
        "Water filtered through activated carbon and structured "
        "using the UMH Pure Gold energiser — a technical conditioning "
        "process that restores the water's natural hexagonal molecular "
        "arrangement."
    )
    for line in _wrap_text(water_body, f_body, text_w):
        draw.text((s + 8, y), line, font=f_body, fill="#444444")
        y += 22
    y += 8

    draw.line([(s, y), (BACK_W - s, y)], fill="#D9BC8A", width=1)
    y += 8

    # --- 3. Ingredients section ---
    draw.text((s + 8, y), "INGREDIENTS", font=f_title, fill=BROWN)
    y += 26

    full_ingredients = (
        f"{BASE_INGREDIENTS}, {cfg['addition']}. {FOOTNOTE}"
    )
    for line in _wrap_text(full_ingredients, f_body, text_w):
        draw.text((s + 8, y), line, font=f_body, fill="#444444")
        y += 22
    y += 8

    draw.line([(s, y), (BACK_W - s, y)], fill="#D9BC8A", width=1)
    y += 8

    # --- 4. Legal footer ---
    footer_lines = [
        "Store refrigerated after opening",
        "Best before: ............  (DD/MM/YYYY)",
        "Contains live cultures  \u00b7  Naturally fermented <0.5% vol",
        "Real Health Kombucha  \u00b7  Caminho de Jangao 154",
        "9360-523 Ponta do Sol  \u00b7  Madeira, Portugal",
    ]
    for line in footer_lines:
        draw.text((s + 8, y), line, font=f_footer, fill="#888888")
        y += 22

    # --- 5. Bottom stripe ---
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
