import argparse
import textwrap
import platform
from PIL import Image, ImageDraw, ImageFont

# ==============================
# ARGUMENT PARSER
# ==============================
parser = argparse.ArgumentParser(
    description="Convert text file to a receipt-size PNG (5cm wide) with optional checklist and Emoji formatting"
)

parser.add_argument("-i", "--input", required=True, help="Input text file")
parser.add_argument("-o", "--output", required=True, help="Output PNG file")
parser.add_argument("--dpi", type=int, default=203, help="Printer DPI (default: 203)")
parser.add_argument("--font", help="Path to TTF/OTF font file (e.g., Segoe UI Emoji)")
parser.add_argument("--font-size", type=int, default=24, help="Font size")
parser.add_argument(
    "-a", "--align", 
    choices=["left", "center", "right"], 
    default="left", 
    help="Text alignment: left, center, or right (default: left)"
)
parser.add_argument("--margin", type=int, default=10, help="Margin in pixels (default: 10)")
parser.add_argument(
    "-c", "--checklist", 
    action="store_true", 
    help="Format the output as a checklist with checkboxes"
)

args = parser.parse_args()

# ==============================
# RECEIPT CONFIG
# ==============================
RECEIPT_WIDTH_MM = 50  # 5 cm
MARGIN = args.margin
LINE_SPACING = 6 if args.checklist else 4

# Convert mm → pixels
WIDTH_PX = int(RECEIPT_WIDTH_MM * args.dpi / 25.4)

# ==============================
# LOAD TEXT
# ==============================
with open(args.input, "r", encoding="utf-8") as f:
    text = f.read()

# ==============================
# LOAD FONT (With Emoji Fallbacks)
# ==============================
if args.font:
    font = ImageFont.truetype(args.font, args.font_size)
else:
    sys_os = platform.system()
    try:
        if sys_os == "Windows":
            font = ImageFont.truetype("seguiemj.ttf", args.font_size)  # Segoe UI Emoji
        elif sys_os == "Darwin":
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", args.font_size)
        else:
            font = ImageFont.truetype("DejaVuSans.ttf", args.font_size)
    except IOError:
        try:
            font = ImageFont.load_default(size=args.font_size)
        except TypeError:
            font = ImageFont.load_default()

# Dynamically scale checkbox dimensions if checklist mode is active
box_size = int(args.font_size * 0.65) if args.checklist else 0
box_padding = int(args.font_size * 0.4) if args.checklist else 0
box_thickness = max(2, int(args.font_size * 0.08))

# ==============================
# MEASURE & WRAP TEXT
# ==============================
temp_img = Image.new("RGBA", (WIDTH_PX, 1000), (255, 255, 255, 255))
draw = ImageDraw.Draw(temp_img)

avg_char_width = draw.textlength(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ", font=font
) / 26

available_text_width = WIDTH_PX - (2 * MARGIN) - (box_size + box_padding)
chars_per_line = max(1, int(available_text_width / avg_char_width))

structured_items = []
total_line_count = 0

for p in text.split("\n"):
    wrapped = textwrap.wrap(p, width=chars_per_line) or [""]
    structured_items.append(wrapped)
    total_line_count += len(wrapped)

line_height = font.getbbox("Ay")[3]
img_height = (
    total_line_count * (line_height + LINE_SPACING)
    + 2 * MARGIN
)

# ==============================
# CREATE IMAGE & DRAW (RGBA Pipeline)
# ==============================
img = Image.new("RGBA", (WIDTH_PX, img_height), (255, 255, 255, 255))
draw = ImageDraw.Draw(img)

y = MARGIN
for item_lines in structured_items:
    if args.checklist:
        first_line_width = draw.textlength(item_lines[0], font=font)
        total_item_width = box_size + box_padding + first_line_width
        
        if args.align == "left":
            unit_x = MARGIN
        elif args.align == "center":
            unit_x = (WIDTH_PX - total_item_width) / 2
        elif args.align == "right":
            unit_x = WIDTH_PX - MARGIN - total_item_width

        for i, line in enumerate(item_lines):
            text_x = unit_x + box_size + box_padding
            
            if i == 0:
                box_x1 = unit_x
                box_y1 = y + (line_height - box_size) // 2
                draw.rectangle(
                    [box_x1, box_y1, box_x1 + box_size, box_y1 + box_size], 
                    outline=(0, 0, 0, 255), 
                    width=box_thickness
                )
            
            draw.text((text_x, y), line, fill=(0, 0, 0, 255), font=font, embedded_color=True)
            y += line_height + LINE_SPACING
            
    else:
        for line in item_lines:
            line_width = draw.textlength(line, font=font)
            
            if args.align == "left":
                x = MARGIN
            elif args.align == "center":
                x = (WIDTH_PX - line_width) / 2
            elif args.align == "right":
                x = WIDTH_PX - MARGIN - line_width

            draw.text((x, y), line, fill=(0, 0, 0, 255), font=font, embedded_color=True)
            y += line_height + LINE_SPACING

# ==============================
# ESTIMATE PAPER LENGTH
# ==============================
length_mm = (img_height * 25.4) / args.dpi
length_cm = length_mm / 10

# ==============================
# POST-PROCESSING & SAVE
# ==============================
final_greyscale_img = img.convert("L")
final_greyscale_img.save(args.output, dpi=(args.dpi, args.dpi))

print("✅ Receipt image generated with Emoticon support!")
print(f"🧾 Width    : 5 cm ({WIDTH_PX}px)")
print(f"📏 Length   : {length_cm:.1f} cm ({img_height}px)")
print(f"🖨 DPI      : {args.dpi}")
print(f"📐 Align    : {args.align}")
print(f"🔲 Margin   : {args.margin}px")
print(f"📋 Mode     : {'Checklist' if args.checklist else 'Standard Text'}")
print(f"📄 File     : {args.output}")