# Real Health Kombucha — Label Design Spec
**Date:** 2026-03-22
**Status:** Approved

---

## Overview

Design and generate print-ready front + back labels for 6 kombucha flavours. Labels are generated as Python PIL scripts, producing high-resolution PNG files. Each flavour has a unique watercolor-style illustration and colour palette. AI image prompts are also provided per flavour for optional illustration upgrade.

---

## Bottle Specs

| Property | Value |
|---|---|
| Volume | 250 ml |
| Cap | 28 mm standard metal screw cap |
| Label system | Front + back (two separate labels) |
| Front label live area | 70 × 90 mm |
| Back label live area | 70 × 75 mm |
| Print bleed | 3 mm on all sides |
| Output resolution | 300 DPI |
| **Front canvas (incl. bleed)** | **896 × 1133 px** (live area 826 × 1063 px, safe zone starts 35 px from each edge) |
| **Back canvas (incl. bleed)** | **896 × 956 px** (live area 826 × 886 px, safe zone starts 35 px from each edge) |

---

## Brand Identity

- **Brand name:** Real Health Kombucha
- **Brand colours:** Cream `#F5F0E8`, Espresso brown `#3D2B1F`, Saddle brown `#8B4513`
- **Fonts:** Georgia (serif) for all text — regular and italic
- **Tagline:** *Handcrafted in Madeira*
- **Producer:** Real Health Kombucha, Caminho de Jangao 154, 9360-523 Ponta do Sol, Madeira, Portugal
- **Existing logo assets:** `assets/design-logos/logo_transparent_highres.png`

---

## Front Label Layout

All coordinates are within the live area (35 px safe zone inset from canvas edge). Zones from top to bottom:

1. **Flavour-colour stripe** — 8 px height, colour = flavour accent (mid tone)
2. **Logo zone** — sunburst + Madeira island silhouette + diamond rules + `REAL HEALTH` (spaced caps, Georgia bold, 52 pt / ~217 px at 300 DPI) — drawn using shared functions from `src/label_utils.py` (see Implementation Notes)
3. **KOMBUCHA** — Georgia bold, 38 pt / ~159 px, letter-spacing 8, colour `#8B4513`
4. **Watercolor illustration zone** — occupies ~45% of label height; Python PIL generated (layered translucent shapes + gaussian blur) or AI-generated image alpha-composited over `#FFFDF8` before placement (see Implementation Notes)
5. **Flavour band** — flavour accent colour background; flavour name in white spaced caps (Georgia bold, 24 pt / ~100 px) + *Handcrafted in Madeira* italic sub-line (Georgia italic, 14 pt / ~58 px)
6. **Flavour-colour stripe** — 8 px, same as top stripe
7. **Net quantity** — `250 ml e` printed in bottom-right corner of live area, Georgia regular, 10 pt / ~42 px, colour `#3D2B1F` (EU Reg. 1169/2011 Art. 9(1)(e))

**Label background:** Warm cream `#FFFDF8`

---

## Back Label Layout

All coordinates within live area. Font sizes set to ensure physical x-height ≥ 1.2 mm at print size (EU Reg. 1169/2011 Art. 13(2)), which requires ≥ 14 px / 5 pt at 300 DPI for 70 mm label width. Zones from top to bottom:

1. **Flavour-colour stripe** — 6 px
2. **Structured Water section**
   - Small icon: `assets/water-colors/07-hexagonal-water.png` — cropped to ~40×40 px, placed left of the section title
   - Section title: `STRUCTURED WATER` — Georgia bold, 16 px / 5.5 pt, colour `#3D2B1F`
   - Body (16 px / 5.5 pt, colour `#444`): *Water filtered through activated carbon and structured using the UMH Pure Gold energiser — a technical conditioning process that restores the water's natural hexagonal molecular arrangement.*
   - ⚠️ **Legal note:** This text describes only the production process. It makes no health or functional benefit claim and is intended to be compliant with EC Regulation 1924/2006. Obtain sign-off from a food regulatory advisor before first print run.
3. **Ingredients section** (EU Reg. 1169/2011 compliant)
   - Section title: `INGREDIENTS` — Georgia bold, 16 px / 5.5 pt
   - Body text: Georgia regular, 14 px / 5 pt, colour `#444`, line-height 1.5
   - Listed in descending order by weight — see per-flavour list below
   - Latin botanical names in italics
   - Sugar footnote: *\*Partially consumed during fermentation*
   - **Allergen rendering:** No current ingredients trigger EU Annex II allergens. If a future flavour addition does, the code must render allergen names in **bold** using a two-pass text approach (draw regular text, overlay bold span at measured x-offset). Document this in code as `# EU allergen emphasis — Reg. 1169/2011 Art. 21`.
4. **Legal footer** — Georgia regular, 14 px / 5 pt, colour `#999` (mandatory particulars — best before, storage, address, alcohol vol — must meet EU Reg. 1169/2011 Art. 13(2) minimum x-height)
   - *Store refrigerated after opening*
   - *Best before: ............* (dotted line — date handwritten by producer at bottling; format: DD/MM/YYYY)
   - *Contains live cultures · Naturally fermented <0.5% vol*
   - *Real Health Kombucha · Caminho de Jangao 154*
   - *9360-523 Ponta do Sol · Madeira, Portugal*
5. **Flavour-colour stripe** — 6 px

**No health claims** — compliant with EU Regulation EC 1924/2006.

---

## Flavour Colour Palettes

The **Band BG** column drives the flavour band background on both front and back labels. The **Mid** colour drives the top/bottom accent stripes and illustration mid-tones. The **Dark** colour drives illustration shadows. For Green Mandarine, the dual-tone design (green band, orange dark) is intentional — the fruit transitions from green skin to orange flesh.

| Flavour | Light | Mid (stripes) | Dark (shadows) | Band BG |
|---|---|---|---|---|
| Ginger | `#FDFAE8` | `#EAD878` | `#C4A030` | `#C4A030` |
| Wild Orange | `#FFF3D0` | `#FFAA40` | `#FF7000` | `#FF7000` |
| Lime | `#F4FAC0` | `#A8D428` | `#5A8A10` | `#5A8A10` |
| Turmeric + Lemon | `#FFFBA0` | `#F5E020` | `#C8A000` | `#C8A000` |
| Metabolic Boost | `#FFE8C0` | `#FF4500` | `#8B0000` | `#CC2000` (intentionally darker than Mid — "fire" gradient effect) |
| Green Mandarine | `#E8F8D0` | `#8CC840` | `#F0882A` | `#6A9010` (green band; orange Dark used for illustration shadow only) |

---

## Ingredients Lists (EU-compliant)

All flavours share the same base, with flavour-specific additions at the end in descending order by weight.

**Base (all flavours):**
> Filtered structured water, fermented green tea *(Camellia sinensis)*, raw cane sugar\*, kombucha culture (SCOBY)

**Per flavour additions:**

| Flavour | Addition |
|---|---|
| Ginger | ginger *(Zingiber officinale)* |
| Wild Orange | wild orange juice *(Citrus sinensis)* |
| Lime | lime juice *(Citrus aurantifolia)* |
| Turmeric + Lemon | lemon juice *(Citrus limon)*, turmeric *(Curcuma longa)* |
| Metabolic Boost | grapefruit juice *(Citrus paradisi)*, lemon juice *(Citrus limon)*, peppermint *(Mentha piperita)*, ginger *(Zingiber officinale)*, cinnamon *(Cinnamomum verum)* |
| Green Mandarine | green mandarine juice *(Citrus reticulata)* |

> Note: If wild orange is sourced from *Citrus aurantium* (bitter/Seville orange) rather than *Citrus sinensis*, update the Latin name accordingly before print.

---

## Watercolor Illustration Subjects (Python PIL)

Each illustration uses the flavour's light→mid→dark palette with layered translucent ellipses, radial gradients and gaussian blur (`ImageFilter.GaussianBlur(radius=8)`) to simulate a watercolor wash. Leaf/botanical accents added per flavour.

| Flavour | Illustration subject | Botanical accent |
|---|---|---|
| Ginger | Knobby ginger root, cross-section showing fibrous interior | Small green leaf sprigs |
| Wild Orange | Whole orange + halved slice showing segments | Leaf and white blossom |
| Lime | Halved lime + wedge | Lime leaf |
| Turmeric + Lemon | Turmeric root piece + lemon half | Turmeric leaf |
| Metabolic Boost | Grapefruit half + cinnamon stick + peppermint sprig | Multi-element composition |
| Green Mandarine | Whole mandarine on branch with leaves | Green mandarine leaf |

---

## AI Image Prompts (Midjourney / DALL-E 3)

All watercolor images are present in `assets/water-colors/` as RGB PNGs (white background, 1024 px+). The label script crops and pastes them directly onto the cream label background — no alpha compositing needed. Scale to fit the illustration zone maintaining aspect ratio, centre-crop if needed. See the flavour→file mapping in the File Output Structure section.

**Ginger:**
> *Delicate watercolor illustration of a fresh ginger root, knobby and organic, warm cream and golden-yellow tones with small green leaf sprigs, white background, botanical art style, high detail, no text*

**Wild Orange:**
> *Watercolor illustration of a whole wild orange and a halved orange slice showing the segments, vibrant orange and peach tones, with a small leaf and white blossom, white background, botanical art style, high detail, no text*

**Lime:**
> *Watercolor illustration of a halved lime and a lime wedge, fresh yellow-green tones, with a lime leaf, white background, botanical illustration style, high detail, no text*

**Turmeric + Lemon:**
> *Watercolor illustration of a turmeric root and a halved lemon, bright sunshine yellow tones, with a turmeric leaf, white background, botanical art style, high detail, no text*

**Metabolic Boost:**
> *Watercolor illustration of a grapefruit half, cinnamon sticks, a peppermint sprig and a small piece of ginger root, fiery orange-red and warm cream tones, white background, botanical art style, high detail, no text*

**Green Mandarine:**
> *Watercolor illustration of a green mandarine on a branch with leaves, fresh green blending into orange tones, white background, botanical illustration style, high detail, no text*

---

## File Output Structure

```
output/labels/
  ginger_front.png
  ginger_back.png
  wild_orange_front.png
  wild_orange_back.png
  lime_front.png
  lime_back.png
  turmeric_lemon_front.png
  turmeric_lemon_back.png
  metabolic_boost_front.png
  metabolic_boost_back.png
  green_mandarine_front.png
  green_mandarine_back.png

assets/water-colors/        ← actual watercolor images (already present)
  01-ginger.png             1024×1024 RGB
  02-wild-orange.png        1024×1024 RGB
  03-green-mandarine.png    1024×1536 RGB
  04-lemon-turmeric.png     1024×1024 RGB
  05-meta-boost.png         1024×1536 RGB
  06-lime.png               1024×1536 RGB
  07-hexagonal-water.png    1024×1536 RGB  ← used as icon on back label
```

**Flavour → image file mapping:**

| Flavour key | Image file |
|---|---|
| ginger | `assets/water-colors/01-ginger.png` |
| wild_orange | `assets/water-colors/02-wild-orange.png` |
| green_mandarine | `assets/water-colors/03-green-mandarine.png` |
| turmeric_lemon | `assets/water-colors/04-lemon-turmeric.png` |
| metabolic_boost | `assets/water-colors/05-meta-boost.png` |
| lime | `assets/water-colors/06-lime.png` |

---

## Implementation Notes

### Code Architecture

- **`src/label_utils.py`** — new shared module containing:
  - `draw_sunburst(draw, cx, cy, ...)` — extracted from `generate_logo_C.py`
  - `draw_island(draw, cx, cy, ...)` — extracted from `generate_logo_C.py`
  - `draw_diamond_rule(draw, cx, y, width, color)` — extracted from `generate_logo_C.py`
  - `draw_spaced_text(draw, x, y, text, font, color, spacing)` — extracted from `generate_logo_C.py`
  - `draw_watercolor_illustration(img, flavour_key, palette, bbox)` — PIL watercolor generator
  - `composite_ai_image(label_img, ai_path, bbox, bg="#FFFDF8")` — alpha-composite AI image over label background

- **`generate_labels.py`** — main script with `FLAVOURS` config dict (one entry per flavour), iterates to produce all 12 output files

- **`generate_logo_C.py`** — left unchanged; will import shared functions from `label_utils.py` once extracted

### AI Image Compositing

```python
# Composite AI watercolor image over label background
from PIL import Image

def composite_ai_image(label_img, ai_path, bbox, bg="#FFFDF8"):
    ai = Image.open(ai_path).convert("RGBA")
    ai = ai.resize((bbox[2]-bbox[0], bbox[3]-bbox[1]), Image.LANCZOS)
    bg_layer = Image.new("RGBA", ai.size, bg)
    composited = Image.alpha_composite(bg_layer, ai).convert("RGB")
    label_img.paste(composited, (bbox[0], bbox[1]))
```

### Font Size Reference (300 DPI, 70 mm label width)

| Element | pt | px | Physical size |
|---|---|---|---|
| REAL HEALTH | 52 pt | 217 px | ~4.6 mm cap height |
| KOMBUCHA | 38 pt | 159 px | ~3.4 mm cap height |
| Flavour name (band) | 24 pt | 100 px | ~2.1 mm cap height |
| Tagline italic | 14 pt | 58 px | ~1.2 mm x-height ✓ |
| Back section titles | 5.5 pt | 16 px | ~1.4 mm x-height ✓ |
| Back body text | 5 pt | 14 px | ~1.2 mm x-height ✓ (legal minimum) |
| Legal footer | 5 pt | 14 px | ~1.2 mm x-height ✓ (mandatory particulars must meet minimum) |
