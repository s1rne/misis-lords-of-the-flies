#!/usr/bin/env python3
"""Generate personalized diplomas by filling blanks in template."""

from PIL import Image, ImageDraw, ImageFont
import os

TEAM_MEMBERS = [
    "Андрей Андреев",
    "Николай Боровец",
    "Илья Сироткин",
    "Плешевич Милена",
    "Александр Симаранов",
    "Саргин Ярослав",
]

TEMPLATE_PATH = "/Users/alexander/misis-lords-of-the-flies/дипломы/drone_ros2.jpg"
OUTPUT_DIR = "/Users/alexander/misis-lords-of-the-flies/дипломы/generated"

os.makedirs(OUTPUT_DIR, exist_ok=True)
template = Image.open(TEMPLATE_PATH)
width, height = template.size

# Load fonts
try:
    name_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf", 40)
    place_font = ImageFont.truetype("/System/Library/Fonts/Times.ttc", 26)
except:
    name_font = ImageFont.load_default()
    place_font = ImageFont.load_default()

BLUE = (61, 155, 233)
BLACK = (0, 0, 0)

def generate_diploma(name):
    """Fill name and place in diploma template."""
    diploma = template.copy()
    draw = ImageDraw.Draw(diploma)

    # Name position (first blank line after "награждается")
    name_y = 427
    bbox = draw.textbbox((0, 0), name, font=name_font)
    name_x = (width - (bbox[2] - bbox[0])) // 2
    draw.text((name_x, name_y), name, fill=BLACK, font=name_font)

    # Place position - "2-е" fills the blank in "за ___ место" (same line as за/место)
    place_y = 671
    place_x = 305
    draw.text((place_x, place_y), "2-е", fill=BLUE, font=place_font)

    filename = f"{name.replace(' ', '_')}.jpg"
    diploma.save(os.path.join(OUTPUT_DIR, filename), quality=95)
    print(f"Generated: {filename}")

for member in TEAM_MEMBERS:
    generate_diploma(member)

print(f"\nAll {len(TEAM_MEMBERS)} diplomas created")
