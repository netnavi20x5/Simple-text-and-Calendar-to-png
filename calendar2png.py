import argparse
import calendar
import datetime
from PIL import Image, ImageDraw, ImageFont

# ==============================
# ARGUMENT PARSER
# ==============================
parser = argparse.ArgumentParser(
    description="Convert a specific month to a receipt-size calendar PNG (5cm wide) with gridlines."
)

current_date = datetime.date.today()

parser.add_argument("-o", "--output", required=True, help="Output PNG file")
parser.add_argument("-i", "--input", help="Optional text file with dates to grey out (format: dd-mm-yyyy)")
parser.add_argument("-y", "--year", type=int, default=current_date.year, help=f"Year for the calendar (default: {current_date.year})")
parser.add_argument("-m", "--month", type=int, default=current_date.month, help=f"Month for the calendar 1-12 (default: {current_date.month})")
parser.add_argument("--dpi", type=int, default=203, help="Printer DPI (default: 203)")
parser.add_argument("--font", help="Path to TTF font file")
parser.add_argument("--font-size", type=int, default=22, help="Font size (default: 22)")
parser.add_argument("--margin", type=int, default=15, help="Margin in pixels (default: 15)")
parser.add_argument("--greyscale", type=int, default=50, help="Shading darkness percentage for matched dates 0-100 (default: 50)")

args = parser.parse_args()

# ==============================
# RECEIPT CONFIG
# ==============================
RECEIPT_WIDTH_MM = 50  # 5 cm
MARGIN = args.margin

# Convert mm → pixels
WIDTH_PX = int(RECEIPT_WIDTH_MM * args.dpi / 25.4)

# ==============================
# PARSE INPUT HIGHLIGHT DATES
# ==============================
highlighted_days = set()

if args.input:
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    day_part, month_part, year_part = map(int, line.split("-"))
                    if year_part == args.year and month_part == args.month:
                        highlighted_days.add(day_part)
                except ValueError:
                    continue
    except FileNotFoundError:
        print(f"\n❌ Error: Input file '{args.input}' not found.")
        print("💡 Correct command usage example:")
        print("   python calendar_gen.py -o marked_may.png -i holidays.txt --greyscale 40\n")
        print("▶️ Continuing by generating a clean calendar grid...\n")

# ==============================
# LOAD FONT
# ==============================
if args.font:
    font = ImageFont.truetype(args.font, args.font_size)
else:
    try:
        font = ImageFont.load_default(size=args.font_size)
    except TypeError:
        font = ImageFont.load_default()

# ==============================
# CALENDAR STRUCT & MEASUREMENTS
# ==============================
cal = calendar.Calendar(firstweekday=6)  # Sunday = 6
weeks = cal.monthdayscalendar(args.year, args.month)

line_height = font.getbbox("Ay")[3]
row_height = line_height + 16  
text_y_offset = (row_height - line_height) // 2  

total_rows = 2 + len(weeks)  
img_height = (total_rows * row_height) + (2 * MARGIN)

# ==============================
# CREATE IMAGE & DRAW
# ==============================
img = Image.new("L", (WIDTH_PX, img_height), 255)
draw = ImageDraw.Draw(img)

cell_width = (WIDTH_PX - (2 * MARGIN)) / 7
y = MARGIN

# 1. Draw Month & Year Title Header
month_name = calendar.month_name[args.month].upper()
title_text = f"{month_name} {args.year}"
title_width = draw.textlength(title_text, font=font)
draw.text(((WIDTH_PX - title_width) / 2, y + text_y_offset), title_text, fill=0, font=font)

y += row_height

# Keep track of grid structures
grid_top_y = y
horiz_lines = [grid_top_y]

# 2. Draw Weekday Headers
day_headers = ["S", "M", "T", "W", "T", "F", "S"]
for idx, day_label in enumerate(day_headers):
    cell_x = MARGIN + (idx * cell_width)
    label_width = draw.textlength(day_label, font=font)
    draw.text((cell_x + (cell_width - label_width) / 2, y + text_y_offset), day_label, fill=0, font=font)

y += row_height
horiz_lines.append(y)

# Calculate the pixel shade factor
shade_value = int(255 * (1 - (args.greyscale / 100)))

# 3. Draw Calendar Grid Days & Shading
for week in weeks:
    for idx, day in enumerate(week):
        if day != 0:
            cell_x = MARGIN + (idx * cell_width)
            
            if day in highlighted_days:
                box_x1 = int(cell_x + 1)
                box_y1 = int(y + 1)
                box_x2 = int(cell_x + cell_width - 1)
                box_y2 = int(y + row_height - 1)
                draw.rectangle([box_x1, box_y1, box_x2, box_y2], fill=shade_value)
            
            day_str = str(day)
            day_width = draw.textlength(day_str, font=font)
            draw.text((cell_x + (cell_width - day_width) / 2, y + text_y_offset), day_str, fill=0, font=font)
            
    y += row_height
    horiz_lines.append(y)

grid_bottom_y = y

# ==============================
# DRAW GRID LINES OVERLAY
# ==============================
for i in range(8):
    x = int(MARGIN + (i * cell_width))
    draw.line([(x, grid_top_y), (x, grid_bottom_y)], fill=0, width=1)

for hy in horiz_lines:
    draw.line([(MARGIN, int(hy)), (WIDTH_PX - MARGIN, int(hy))], fill=0, width=1)

# ==============================
# ESTIMATE PAPER LENGTH
# ==============================
length_mm = (img_height * 25.4) / args.dpi
length_cm = length_mm / 10

# ==============================
# SAVE
# ==============================
img.save(args.output, dpi=(args.dpi, args.dpi))

print("✅ Receipt Calendar generated successfully!")
print(f"📅 Target   : {month_name} {args.year}")
print(f"🧾 Width    : 5 cm ({WIDTH_PX}px)")
print(f"📏 Length   : {length_cm:.1f} cm ({img_height}px)")
print(f"🎨 Grey Fill: {args.greyscale}% intensity")
print(f"📄 Saved to : {args.output}")