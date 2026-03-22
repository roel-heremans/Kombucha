# Kombucha Label Generator Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate print-ready 300 DPI front + back PNG labels for 6 kombucha flavours using Python PIL, incorporating real watercolor images and the existing brand logo design.

**Architecture:** A shared `src/label_utils.py` module holds all reusable drawing primitives (extracted from `generate_logo_C.py`). A single `generate_labels.py` script drives generation for all 6 flavours using a `FLAVOURS` config dict, producing 12 output PNGs in `output/labels/`.

**Tech Stack:** Python 3, Pillow (PIL), Georgia TTF fonts (system fonts on macOS), existing assets in `assets/design-logos/` and `assets/water-colors/`.

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `src/label_utils.py` | **Create** | All reusable drawing primitives: sunburst, island, diamond rules, spaced text, watercolor paste, text runs |
| `generate_labels.py` | **Create** | FLAVOURS config dict + top-level generation loop |
| `tests/test_label_utils.py` | **Create** | Unit tests for drawing primitives |
| `tests/test_generate_labels.py` | **Create** | Integration tests: correct canvas size, file existence |
| `generate_logo_C.py` | **Modify** | Import shared functions from `label_utils.py` instead of inline definitions |
| `output/labels/` | **Create dir** | 12 output PNG files |

---

## Constants Reference

```
BLEED            = 35 px  (3 mm at 300 DPI)
FRONT_W, FRONT_H = 896, 1133 px   (incl. bleed)
BACK_W,  BACK_H  = 896,  956 px   (incl. bleed)
LIVE_W           = 826 px  (= 896 - 2×35)
SAFE             = 35 px   (inset from canvas edge to live area)

Brand colours:
  CREAM    = "#FFFDF8"   (label background)
  BROWN    = "#3D2B1F"   (primary / bars)
  AMBER    = "#8B4513"   (secondary / KOMBUCHA text)

Font sizes (PIL pixels at 300 DPI = pt × 300/72):
  REAL HEALTH    → 217 px  (52 pt)
  KOMBUCHA       → 158 px  (38 pt)
  Flavour name   → 100 px  (24 pt)
  Tagline italic →  58 px  (14 pt)
  Back titles    →  22 px  (5.5 pt × 300/72 ≈ 23; use 22 for clean render)
  Back body/footer→ 19 px  (≥14 px legal minimum; 19 px gives readable text)

Font paths (macOS):
  GEORGIA        = "/System/Library/Fonts/Supplemental/Georgia.ttf"
  GEORGIA_BOLD   = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
  GEORGIA_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"
```

---

## Task 1: Create `src/label_utils.py` — drawing primitives

**Files:**
- Create: `src/label_utils.py`
- Create: `tests/test_label_utils.py`

- [ ] **Step 1.1: Write failing tests for `load_font`**

```python
# tests/test_label_utils.py
from PIL import ImageFont
from src.label_utils import load_font

def test_load_font_returns_font():
    font = load_font(size=40, bold=False)
    assert font is not None

def test_load_font_bold():
    font = load_font(size=40, bold=True)
    assert font is not None

def test_load_font_italic():
    font = load_font(size=40, italic=True)
    assert font is not None
```

- [ ] **Step 1.2: Run tests — verify FAIL**

```bash
cd /Users/roel.heremans/Documents/PersonalRepos/Kombucha
python -m pytest tests/test_label_utils.py -v
```
Expected: `ModuleNotFoundError: No module named 'src.label_utils'`

- [ ] **Step 1.3: Create `src/label_utils.py` with `load_font`**

```python
# src/label_utils.py
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
```

- [ ] **Step 1.4: Run tests — verify PASS**

```bash
python -m pytest tests/test_label_utils.py::test_load_font_returns_font tests/test_label_utils.py::test_load_font_bold tests/test_label_utils.py::test_load_font_italic -v
```
Expected: 3 PASSED

- [ ] **Step 1.5: Add tests for `draw_spaced_text` and `spaced_text_width`**

```python
# append to tests/test_label_utils.py
from PIL import Image, ImageDraw
from src.label_utils import draw_spaced_text, spaced_text_width

def test_spaced_text_width_nonzero():
    font = load_font(size=40)
    w = spaced_text_width("HELLO", font, spacing=5)
    assert w > 0

def test_draw_spaced_text_does_not_raise():
    img = Image.new("RGB", (400, 100), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    font = load_font(size=40)
    draw_spaced_text(draw, 10, 10, "HELLO", font, "#000000", spacing=5)
```

- [ ] **Step 1.6: Implement `draw_spaced_text` and `spaced_text_width`**

Add to `src/label_utils.py`:

```python
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
```

- [ ] **Step 1.7: Add tests for `draw_diamond_rule`**

```python
from src.label_utils import draw_diamond_rule

def test_draw_diamond_rule_does_not_raise():
    img = Image.new("RGB", (400, 100), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw_diamond_rule(draw, cx=200, y=50, width=300, color="#8B4513")
```

- [ ] **Step 1.8: Implement `draw_diamond_rule`**

```python
def draw_diamond_rule(draw: ImageDraw.ImageDraw, cx: int, y: int,
                      width: int, color: str, diamond_size: int = 5) -> None:
    x0, x1 = cx - width // 2, cx + width // 2
    draw.line([(x0, y), (x1, y)], fill=color, width=1)
    ds = diamond_size
    for dx in [x0, x1]:
        draw.polygon([(dx, y - ds), (dx + ds, y), (dx, y + ds), (dx - ds, y)], fill=color)
```

- [ ] **Step 1.9: Add tests for `draw_sunburst` and `draw_island`**

```python
from src.label_utils import draw_sunburst, draw_island

def test_draw_sunburst_does_not_raise():
    img = Image.new("RGB", (400, 400), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw_sunburst(draw, cx=200, cy=200, r_outer_long=120,
                  r_outer_short=90, r_inner=40, ray_count=30,
                  color="#3D2B1F", bg="#FFFDF8")

def test_draw_island_does_not_raise():
    img = Image.new("RGB", (400, 400), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw_island(draw, cx=200, cy=200, w=90, h=34,
                tilt_deg=4, color="#3D2B1F")
```

- [ ] **Step 1.10: Implement `draw_sunburst` and `draw_island`**

```python
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
```

- [ ] **Step 1.11: Add test and implement `paste_watercolor`**

```python
# test
from src.label_utils import paste_watercolor

def test_paste_watercolor_fills_bbox():
    label = Image.new("RGB", (826, 1063), "#FFFDF8")
    bbox = (0, 300, 826, 780)
    paste_watercolor(label, "assets/water-colors/01-ginger.png", bbox)
    # Pixel in bbox should no longer be pure cream
    px = label.getpixel((413, 540))
    assert px != (255, 253, 248)
```

```python
# implementation — add to src/label_utils.py
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
```

- [ ] **Step 1.12: Run all label_utils tests — all PASS**

```bash
python -m pytest tests/test_label_utils.py -v
```
Expected: all tests PASS

- [ ] **Step 1.13: Commit**

```bash
git add src/label_utils.py tests/test_label_utils.py
git commit -m "feat: add label_utils.py with shared drawing primitives and tests"
```

---

## Task 2: Create `generate_labels.py` skeleton with FLAVOURS config

**Files:**
- Create: `generate_labels.py`
- Create: `tests/test_generate_labels.py`

- [ ] **Step 2.1: Write failing integration tests**

```python
# tests/test_generate_labels.py
import os
import pytest
from PIL import Image

OUTPUT_DIR = "output/labels"

EXPECTED_FILES = [
    "ginger_front.png", "ginger_back.png",
    "wild_orange_front.png", "wild_orange_back.png",
    "lime_front.png", "lime_back.png",
    "turmeric_lemon_front.png", "turmeric_lemon_back.png",
    "metabolic_boost_front.png", "metabolic_boost_back.png",
    "green_mandarine_front.png", "green_mandarine_back.png",
]

@pytest.mark.parametrize("filename", EXPECTED_FILES)
def test_output_file_exists(filename):
    path = os.path.join(OUTPUT_DIR, filename)
    assert os.path.exists(path), f"Missing: {path}"

@pytest.mark.parametrize("filename", [f for f in EXPECTED_FILES if "front" in f])
def test_front_label_dimensions(filename):
    img = Image.open(os.path.join(OUTPUT_DIR, filename))
    assert img.size == (896, 1133), f"{filename}: expected 896×1133, got {img.size}"

@pytest.mark.parametrize("filename", [f for f in EXPECTED_FILES if "back" in f])
def test_back_label_dimensions(filename):
    img = Image.open(os.path.join(OUTPUT_DIR, filename))
    assert img.size == (896, 956), f"{filename}: expected 896×956, got {img.size}"
```

- [ ] **Step 2.2: Run tests — verify FAIL**

```bash
python -m pytest tests/test_generate_labels.py -v
```
Expected: all 12 file-existence tests FAIL (files not yet generated)

- [ ] **Step 2.3: Create `generate_labels.py` with FLAVOURS config dict**

```python
# generate_labels.py
"""
Generate print-ready front + back labels for all Real Health Kombucha flavours.
Output: output/labels/<flavour>_front.png and _back.png at 896×1133 / 896×956 px (300 DPI, 3 mm bleed).
"""
import os
from PIL import Image

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

def build_front_label(key: str, cfg: dict) -> Image.Image:
    img = Image.new("RGB", (FRONT_W, FRONT_H), CREAM)
    # TODO: implement in Task 3
    return img

def build_back_label(key: str, cfg: dict) -> Image.Image:
    img = Image.new("RGB", (BACK_W, BACK_H), CREAM)
    # TODO: implement in Task 4
    return img

if __name__ == "__main__":
    main()
```

- [ ] **Step 2.4: Run `generate_labels.py` to create blank output files**

```bash
python generate_labels.py
```
Expected: `output/labels/` contains 12 blank cream PNG files

- [ ] **Step 2.5: Run dimension tests — verify PASS**

```bash
python -m pytest tests/test_generate_labels.py -v
```
Expected: all 12 `test_output_file_exists` and all 12 dimension tests PASS

- [ ] **Step 2.6: Commit**

```bash
git add generate_labels.py tests/test_generate_labels.py output/labels/.gitkeep
git commit -m "feat: add label generator skeleton with FLAVOURS config and dimension tests"
```

---

## Task 3: Implement `build_front_label`

**Files:**
- Modify: `generate_labels.py` — replace `build_front_label` stub

- [ ] **Step 3.1: Write a visual regression test for front label**

Add to `tests/test_generate_labels.py`:

```python
def test_front_label_not_blank():
    """Front label must contain non-cream pixels (logo + illustration rendered)."""
    img = Image.open(os.path.join(OUTPUT_DIR, "wild_orange_front.png"))
    pixels = list(img.getdata())
    non_cream = [p for p in pixels if p != (255, 253, 248)]
    assert len(non_cream) > 5000, "Front label appears blank"

def test_front_label_stripe_color():
    """Top stripe (row 0) should match flavour mid colour, not cream."""
    img = Image.open(os.path.join(OUTPUT_DIR, "wild_orange_front.png"))
    top_pixel = img.getpixel((448, 2))  # centre of top stripe
    assert top_pixel != (255, 253, 248), "Top stripe not rendered"
```

- [ ] **Step 3.2: Run new tests — verify FAIL (blank labels)**

```bash
python -m pytest tests/test_generate_labels.py::test_front_label_not_blank tests/test_generate_labels.py::test_front_label_stripe_color -v
```
Expected: FAIL

- [ ] **Step 3.3: Implement `build_front_label` in `generate_labels.py`**

Replace the stub with:

```python
from PIL import ImageDraw
from src.label_utils import (
    load_font, draw_spaced_text, spaced_text_width,
    draw_diamond_rule, draw_sunburst, draw_island, paste_watercolor,
)

def build_front_label(key: str, cfg: dict) -> Image.Image:
    img  = Image.new("RGB", (FRONT_W, FRONT_H), CREAM)
    draw = ImageDraw.Draw(img)
    c    = cfg["colors"]
    s    = SAFE  # shorthand for live area inset

    # --- Fonts ---
    f_real_health = load_font(217, bold=True)
    f_kombucha    = load_font(158, bold=True)
    f_flavour     = load_font(100, bold=True)
    f_tagline     = load_font(58,  italic=True)
    f_qty         = load_font(42)

    # --- 1. Flavour colour stripe — top ---
    draw.rectangle([0, 0, FRONT_W, s - 1], fill=c["mid"])

    # --- 2. Logo zone ---
    # Sunburst centre
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
    band_height  = 100 + 40 + 20   # flavour name + tagline + padding
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
```

- [ ] **Step 3.4: Regenerate labels and run tests**

```bash
python generate_labels.py
python -m pytest tests/test_generate_labels.py -v
```
Expected: all tests PASS including `test_front_label_not_blank` and `test_front_label_stripe_color`

- [ ] **Step 3.5: Visually inspect output**

```bash
open output/labels/wild_orange_front.png
open output/labels/ginger_front.png
open output/labels/lime_front.png
```
Check: logo visible, KOMBUCHA large, watercolor image present, flavour band with correct colour at bottom.

- [ ] **Step 3.6: Commit**

```bash
git add generate_labels.py src/label_utils.py
git commit -m "feat: implement front label layout with logo, watercolor, and flavour band"
```

---

## Task 4: Implement `build_back_label`

**Files:**
- Modify: `generate_labels.py` — replace `build_back_label` stub

- [ ] **Step 4.1: Write failing test for back label content**

Add to `tests/test_generate_labels.py`:

```python
def test_back_label_not_blank():
    img = Image.open(os.path.join(OUTPUT_DIR, "wild_orange_back.png"))
    pixels = list(img.getdata())
    non_cream = [p for p in pixels if p != (255, 253, 248)]
    assert len(non_cream) > 1000, "Back label appears blank"
```

- [ ] **Step 4.2: Run test — verify FAIL**

```bash
python -m pytest tests/test_generate_labels.py::test_back_label_not_blank -v
```

- [ ] **Step 4.3: Implement `build_back_label`**

Add this helper to `generate_labels.py` above `build_back_label`:

```python
def _wrap_text(text: str, font, max_width: int) -> list[str]:
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
```

Then replace the `build_back_label` stub:

```python
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
    text_w = live_w - 20   # inner margin

    # --- 1. Top stripe ---
    draw.rectangle([0, 0, BACK_W, s - 1], fill=c["mid"])

    y = s + 10

    # --- 2. Structured Water section ---
    # Hexagonal water icon (40×40)
    try:
        icon = Image.open(HEXAGONAL_WATER_IMG).convert("RGB")
        icon = icon.resize((40, 40), Image.LANCZOS)
        img.paste(icon, (s + 8, y))
    except Exception:
        pass
    # Title beside icon
    draw.text((s + 56, y + 8), "STRUCTURED WATER",
              font=f_title, fill=BROWN)
    y += 48

    # Body text — wrapped
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

    # Divider
    draw.line([(s, y), (BACK_W - s, y)], fill="#D9BC8A", width=1)
    y += 8

    # --- 3. Ingredients section ---
    draw.text((s + 8, y), "INGREDIENTS", font=f_title, fill=BROWN)
    y += 26

    full_ingredients = (
        f"{BASE_INGREDIENTS}, {cfg['addition']}. {FOOTNOTE}"
    )
    # EU allergen emphasis comment — Reg. 1169/2011 Art. 21
    # No current ingredients trigger Annex II allergens.
    # If a future addition does, render allergen name in bold using a
    # two-pass text approach (see spec Implementation Notes).
    for line in _wrap_text(full_ingredients, f_body, text_w):
        draw.text((s + 8, y), line, font=f_body, fill="#444444")
        y += 22
    y += 8

    # Divider
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
```

- [ ] **Step 4.4: Regenerate labels and run all tests**

```bash
python generate_labels.py
python -m pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 4.5: Visually inspect back labels**

```bash
open output/labels/wild_orange_back.png
open output/labels/metabolic_boost_back.png
```
Check: structured water section with hex icon, ingredients text readable, footer present, stripes match flavour colour.

- [ ] **Step 4.6: Commit**

```bash
git add generate_labels.py
git commit -m "feat: implement back label with structured water, ingredients, and legal footer"
```

---

## Task 5: Final verification — all 12 labels

- [ ] **Step 5.1: Run full test suite**

```bash
python -m pytest tests/ -v
```
Expected: all tests PASS

- [ ] **Step 5.2: Open and visually check all 12 labels**

```bash
open output/labels/ginger_front.png output/labels/ginger_back.png
open output/labels/wild_orange_front.png output/labels/wild_orange_back.png
open output/labels/lime_front.png output/labels/lime_back.png
open output/labels/turmeric_lemon_front.png output/labels/turmeric_lemon_back.png
open output/labels/metabolic_boost_front.png output/labels/metabolic_boost_back.png
open output/labels/green_mandarine_front.png output/labels/green_mandarine_back.png
```

Check for each flavour:
- [ ] Correct stripe colour (top + bottom)
- [ ] Logo (sunburst + island + REAL HEALTH) clearly visible
- [ ] KOMBUCHA large and prominent
- [ ] Watercolor illustration fills the illustration zone
- [ ] Flavour name in correct colour band with "Handcrafted in Madeira"
- [ ] Back: hex water icon + structured water text
- [ ] Back: ingredients list readable
- [ ] Back: legal footer present

- [ ] **Step 5.3: Refactor `generate_logo_C.py` to import from `label_utils`**

Replace the inline definitions in `generate_logo_C.py` with imports:

```python
# At top of generate_logo_C.py, replace the inline draw_* functions with:
from src.label_utils import (
    load_font, draw_spaced_text, spaced_text_width,
    draw_diamond_rule, draw_sunburst, draw_island,
)
```

Then run the logo generator to confirm it still works:

```bash
python generate_logo_C.py
open assets/design-logos/logo_variant_C.png
```

- [ ] **Step 5.4: Final commit**

```bash
git add generate_labels.py generate_logo_C.py src/label_utils.py tests/ output/labels/
git commit -m "feat: complete kombucha label generator — 12 print-ready labels for 6 flavours"
```
