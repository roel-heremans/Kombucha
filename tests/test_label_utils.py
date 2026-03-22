from PIL import ImageFont, Image, ImageDraw
from src.label_utils import (
    load_font,
    draw_spaced_text, spaced_text_width,
    draw_diamond_rule,
    draw_sunburst, draw_island,
    paste_watercolor,
)


def test_load_font_returns_font():
    font = load_font(size=40, bold=False)
    assert font is not None


def test_load_font_bold():
    font = load_font(size=40, bold=True)
    assert font is not None


def test_load_font_italic():
    font = load_font(size=40, italic=True)
    assert font is not None


def test_spaced_text_width_nonzero():
    font = load_font(size=40)
    w = spaced_text_width("HELLO", font, spacing=5)
    assert w > 0


def test_draw_spaced_text_does_not_raise():
    img = Image.new("RGB", (400, 100), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    font = load_font(size=40)
    draw_spaced_text(draw, 10, 10, "HELLO", font, "#000000", spacing=5)


def test_draw_diamond_rule_does_not_raise():
    img = Image.new("RGB", (400, 100), "#FFFFFF")
    draw = ImageDraw.Draw(img)
    draw_diamond_rule(draw, cx=200, y=50, width=300, color="#8B4513")


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


def test_paste_watercolor_fills_bbox():
    label = Image.new("RGB", (826, 1063), "#FFFDF8")
    bbox = (0, 300, 826, 780)
    paste_watercolor(label, "assets/water-colors/01-ginger.png", bbox)
    # Pixel in bbox should no longer be pure cream
    px = label.getpixel((413, 540))
    assert px != (255, 253, 248)
