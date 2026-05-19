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

# Use sans-serif fonts like in example (not serif/italic)
try:
    # Regular sans-serif for name - smaller size like in example
    name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    # Sans-serif for place
    place_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 26)
except:
    name_font = ImageFont.load_default()
    place_font = ImageFont.load_default()

BLUE = (61, 155, 233)
BLACK = (0, 0, 0)
GRAY = (120, 120, 120)

def generate_diploma(name):
    """Fill name and place in diploma template."""
    diploma = template.copy()
    draw = ImageDraw.Draw(diploma)

    # Name position - first blank line after "награждается" (~y=427)
    name_y = 428
    bbox = draw.textbbox((0, 0), name, font=name_font)
    name_width = bbox[2] - bbox[0]
    name_x = (width - name_width) // 2
    draw.text((name_x, name_y), name, fill=BLACK, font=name_font)

    # Underline under name
    underline_y = name_y + 40
    draw.line([(name_x - 20, underline_y), (name_x + name_width + 20, underline_y)],
              fill=GRAY, width=1)

    # Place position - "2-е" on same line as "за ___ место"
    place_y = 671
    place_x = 305
    draw.text((place_x, place_y), "2-е", fill=BLUE, font=place_font)

    filename = f"{name.replace(' ', '_')}.jpg"
    diploma.save(os.path.join(OUTPUT_DIR, filename), quality=95)
    print(f"Generated: {filename}")

for member in TEAM_MEMBERS:
    generate_diploma(member)

print(f"\nAll {len(TEAM_MEMBERS)} diplomas created")
