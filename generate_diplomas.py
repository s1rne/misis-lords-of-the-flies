#!/usr/bin/env python3
"""Generate personalized diplomas for hackathon participants."""

from PIL import Image, ImageDraw, ImageFont
import os

# Team members
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

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load template
template = Image.open(TEMPLATE_PATH)
width, height = template.size

# Try to find appropriate fonts
try:
    # Main title font
    title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
    # Name font
    name_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    # Regular text font
    regular_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
except:
    # Fallback to default
    title_font = ImageFont.load_default()
    name_font = ImageFont.load_default()
    regular_font = ImageFont.load_default()

# Color: match the blue from template
BLUE_COLOR = (33, 150, 243)  # RGB blue
BLACK_COLOR = (0, 0, 0)
GRAY_COLOR = (80, 80, 80)

def generate_diploma(name, member_index):
    """Generate diploma for a team member."""
    # Create a copy of template
    diploma = template.copy()
    draw = ImageDraw.Draw(diploma)

    # Calculate proportional positions based on image height
    # Template is approximately 3300px tall
    # Names positioned around 25% down the image
    name_y = int(height * 0.25)
    place_y = int(height * 0.35)

    # Add name - positioned below "награждается"
    # Center the name
    bbox = draw.textbbox((0, 0), name, font=name_font)
    name_width = bbox[2] - bbox[0]
    name_x = (width - name_width) // 2
    draw.text((name_x, name_y), name, fill=BLACK_COLOR, font=name_font)

    # Add underline for name (optional, for elegance)
    line_y = name_y + 50
    draw.line([(400, line_y), (width - 400, line_y)], fill=GRAY_COLOR, width=2)

    # Add place (2-е место) with blue highlight
    place_text = "2-е место"
    bbox = draw.textbbox((0, 0), "за ", font=regular_font)
    bbox_place = draw.textbbox((0, 0), place_text, font=regular_font)
    place_width = bbox_place[2] - bbox_place[0]
    place_x = (width - place_width) // 2

    # Draw "за " in black
    draw.text((place_x, place_y), "за ", fill=BLACK_COLOR, font=regular_font)

    # Draw "2-е" in blue
    bbox2 = draw.textbbox((0, 0), "за ", font=regular_font)
    blue_x = place_x + (bbox2[2] - bbox2[0])
    draw.text((blue_x, place_y), "2-е", fill=BLUE_COLOR, font=regular_font)

    # Draw " место" in black after blue text
    bbox3 = draw.textbbox((0, 0), "2-е", font=regular_font)
    place_x_rest = blue_x + (bbox3[2] - bbox3[0])
    draw.text((place_x_rest, place_y), " место", fill=BLACK_COLOR, font=regular_font)

    # Save diploma
    filename = f"{name.replace(' ', '_')}.jpg"
    output_path = os.path.join(OUTPUT_DIR, filename)
    diploma.save(output_path, quality=95)
    print(f"Generated: {filename}")

# Generate diplomas for each team member
for i, member in enumerate(TEAM_MEMBERS):
    generate_diploma(member, i)

print(f"\nAll {len(TEAM_MEMBERS)} diplomas generated in {OUTPUT_DIR}")
