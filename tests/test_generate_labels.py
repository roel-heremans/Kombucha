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
    assert img.size == (896, 1133), f"{filename}: expected 896x1133, got {img.size}"


@pytest.mark.parametrize("filename", [f for f in EXPECTED_FILES if "back" in f])
def test_back_label_dimensions(filename):
    img = Image.open(os.path.join(OUTPUT_DIR, filename))
    assert img.size == (896, 956), f"{filename}: expected 896x956, got {img.size}"


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


def test_back_label_not_blank():
    img = Image.open(os.path.join(OUTPUT_DIR, "wild_orange_back.png"))
    pixels = list(img.getdata())
    non_cream = [p for p in pixels if p != (255, 253, 248)]
    assert len(non_cream) > 1000, "Back label appears blank"
