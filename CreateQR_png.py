import argparse
import qrcode
from PIL import Image, ImageDraw, ImageFont

# ==============================
# ARGUMENT PARSER
# ==============================
parser = argparse.ArgumentParser(
    description="Convert various data types to a receipt-size QR Code PNG (5cm wide)"
)

parser.add_argument("-o", "--output", required=True, help="Output PNG file")
parser.add_argument("--dpi", type=int, default=203, help="Printer DPI (default: 203)")
parser.add_argument("--margin", type=int, default=20, help="Margin padding in pixels (default: 20)")

# QR Type Selection Group (Mutually Exclusive)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-t", "--text", help="Plain text payload")
group.add_argument("-u", "--url", help="URL link payload (e.g., https://google.com)")
group.add_argument("--wifi", nargs=3, metavar=('SSID', 'PASSWORD', 'SECURITY'),
                   help="Wi-Fi credentials payload. Security options: WPA, WEP, or nopass")
group.add_argument("--email", nargs=3, metavar=('TO', 'SUBJECT', 'BODY'),
                   help="Email payload details")

args = parser.parse_args()

# ==============================
# RECEIPT CONFIG & DPI MATH
# ==============================
RECEIPT_WIDTH_MM = 50  # 5 cm
MARGIN = args.margin

# Convert mm → pixels
WIDTH_PX = int(RECEIPT_WIDTH_MM * args.dpi / 25.4)

# ==============================
# PROCESS PAYLOAD STANDARD FORMATS
# ==============================
qr_payload = ""
content_label = ""

if args.text:
    qr_payload = args.text
    content_label = "TEXT PACKET"

elif args.url:
    # Ensure standard schema exists
    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    qr_payload = url
    content_label = "URL LINK"

elif args.wifi:
    ssid, password, security = args.wifi
    # Standard Wi-Fi Schema: WIFI:S:SSID;T:WPA;P:PASSWORD;;
    qr_payload = f"WIFI:S:{ssid};T:{security};P:{password};;"
    content_label = f"WI-FI ACCESS ({ssid})"

elif args.email:
    to, subject, body = args.email
    # Standard Email Schema: MATMSG:TO:xyz@abc.com;SUB:Hello;BODY:Text;;
    qr_payload = f"MATMSG:TO:{to};SUB:{subject};BODY:{body};;"
    content_label = f"EMAIL PROTOCOL ({to})"

# ==============================
# GENERATE STRUCTURED QR CODE
# ==============================
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_M,  # Medium robust recovery
    box_size=10,
    border=0,  # Controlled manually via receipt MARGIN
)
qr.add_data(qr_payload)
qr.make(fit=True)

# Generate baseline QR Matrix Image (Black/White 1-bit pixel array)
qr_raw_img = qr.make_image(fill_color="black", back_color="white").convert("L")

# Resize the generated matrix to fit beautifully between receipt margins
target_qr_size = WIDTH_PX - (2 * MARGIN)
qr_scaled_img = qr_raw_img.resize((target_qr_size, target_qr_size), Image.Resampling.NEAREST)

# ==============================
# ASSEMBLE RECEIPT CANVAS
# ==============================
# Height is equal to the square QR frame width footprint plus top/bottom padding offsets
img_height = target_qr_size + (2 * MARGIN)

img = Image.new("L", (WIDTH_PX, img_height), 255)
img.paste(qr_scaled_img, (MARGIN, MARGIN))

# ==============================
# ESTIMATE PAPER LENGTH
# ==============================
length_mm = (img_height * 25.4) / args.dpi
length_cm = length_mm / 10

# ==============================
# SAVE
# ==============================
img.save(args.output, dpi=(args.dpi, args.dpi))

print("✅ QR Code receipt image generated successfully!")
print(f"📦 Type     : {content_label}")
print(f"🧾 Width    : 5 cm ({WIDTH_PX}px)")
print(f"📏 Length   : {length_cm:.1f} cm ({img_height}px)")
print(f"🖨 DPI      : {args.dpi}")
print(f"📄 Saved to : {args.output}")