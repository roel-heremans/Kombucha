"""
Real Health Kombucha — Logo
Forest Green & Gold | Half sunburst (top 180°) | Madeira island silhouette
"""

import math, os
from PIL import Image, ImageDraw, ImageFont

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#F5F0E8"   # warm cream
PRIMARY = "#1B3A2D"   # forest green  (island + text)
ACCENT  = "#C9A84C"   # warm gold     (rays + KOMBUCHA)

# ── Canvas ────────────────────────────────────────────────────────────────────
W, H = 800, 800
img  = Image.new("RGB", (W, H), BG)
draw = ImageDraw.Draw(img)

# ── Fonts ─────────────────────────────────────────────────────────────────────
FONT_DIR = "/System/Library/Fonts/Supplemental"

def load_font(name, size):
    for fname in [name, "Times New Roman.ttf"]:
        try:
            return ImageFont.truetype(os.path.join(FONT_DIR, fname), size)
        except Exception:
            pass
    return ImageFont.load_default()

font_rh = load_font("Georgia.ttf", 68)
font_kb = load_font("Georgia.ttf", 28)

# ── Layout ────────────────────────────────────────────────────────────────────
icon_cx = W // 2   # 400
icon_cy = 360      # sunburst origin — rays fan upward, island sits here, text below

# ── Half sunburst: 19 rays spanning -180° → 0° (top semicircle) ──────────────
NUM_RAYS = 24
R_INNER  = 120     # ray base starts beyond island edge
R_LONG   = 230     # long ray length
R_SHORT  = 175     # short ray length

for i in range(NUM_RAYS):
    angle_deg = -180.0 + (180.0 / (NUM_RAYS - 1)) * i   # -180° … 0°
    r_outer   = R_LONG  if i % 2 == 0 else R_SHORT
    half_base = 5       if i % 2 == 0 else 3
    angle_rad = math.radians(angle_deg)
    perp      = angle_rad + math.pi / 2

    bx_l = icon_cx + R_INNER * math.cos(angle_rad) + half_base * math.cos(perp)
    by_l = icon_cy + R_INNER * math.sin(angle_rad) + half_base * math.sin(perp)
    bx_r = icon_cx + R_INNER * math.cos(angle_rad) - half_base * math.cos(perp)
    by_r = icon_cy + R_INNER * math.sin(angle_rad) - half_base * math.sin(perp)
    tx   = icon_cx + r_outer * math.cos(angle_rad)
    ty   = icon_cy + r_outer * math.sin(angle_rad)

    draw.line([(bx_l, by_l), (tx, ty)], fill=ACCENT, width=2)
    draw.line([(bx_r, by_r), (tx, ty)], fill=ACCENT, width=2)

# ── Cream disc: masks ray origins, island drawn on top ───────────────────────
draw.ellipse(
    [icon_cx - 118, icon_cy - 118, icon_cx + 118, icon_cy + 118],
    fill=BG
)

# ── Madeira island silhouette (contour extracted from original logo) ──────────
raw_island = [
    [-43.5,-12.0],[-41.5,-9.0],[-40.5,-3.0],[-35.5,3.0],
    [-25.5,8.0],[-20.5,12.0],[-17.5,12.0],[-8.5,17.0],
    [-3.5,17.0],[3.5,20.0],[6.5,20.0],[9.5,18.0],
    [17.5,20.0],[21.5,19.0],[24.5,16.0],[25.5,12.0],
    [29.5,10.0],[30.5,6.0],[34.5,2.0],[42.5,1.0],
    [39.5,0.0],[35.5,1.0],[32.5,-1.0],[24.5,-2.0],
    [17.5,-7.0],[16.5,-10.0],[9.5,-15.0],[0.5,-13.0],
    [-3.5,-14.0],[-7.5,-11.0],[-13.5,-10.0],[-24.5,-14.0],
    [-30.5,-21.0],[-34.5,-21.0],
]
island_pts = [(icon_cx + rx * 2.2, icon_cy + ry * 2.2) for rx, ry in raw_island]
draw.polygon(island_pts, fill=PRIMARY)

# ── Ponta do Sol marker (brewery location, ~36% from west, ~78% from north) ───
# Geo: 17.08°W, 32.67°N → normalized island coords ≈ (-12, 11) at scale 2.2
dot_x = icon_cx + (-12) * 2.2
dot_y = icon_cy +  11   * 2.2
dot_r = 3   # small radius in px at 800px canvas
draw.ellipse([dot_x - dot_r, dot_y - dot_r, dot_x + dot_r, dot_y + dot_r], fill=ACCENT)

# ── Text: flows directly below the island ────────────────────────────────────
def draw_spaced(text, font, cx, y, color, spacing=8):
    widths = [font.getbbox(c)[2] - font.getbbox(c)[0] for c in text]
    total  = sum(widths) + spacing * (len(text) - 1)
    x      = cx - total / 2
    for i, ch in enumerate(text):
        draw.text((x, y), ch, font=font, fill=color)
        x += widths[i] + spacing

island_bottom = icon_cy + 21 * 2.2   # island lowest point + scale
rh_y          = int(island_bottom) + 38
draw_spaced("REAL HEALTH", font_rh, W // 2, rh_y, PRIMARY, spacing=10)

rh_h      = font_rh.getbbox("A")[3] - font_rh.getbbox("A")[1]
kombucha_y = rh_y + rh_h + 18
draw_spaced("KOMBUCHA", font_kb, W // 2, kombucha_y, ACCENT, spacing=12)

# ── Save ──────────────────────────────────────────────────────────────────────
OUT = "/Users/roel.heremans/Documents/PersonalRepos/Kombucha/assets/design-logos/logo_lowres.png"
os.makedirs(os.path.dirname(OUT), exist_ok=True)
img.save(OUT, "PNG")
print(f"Saved: {OUT}")
