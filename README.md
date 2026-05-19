"# Simple-text-and-Calendar-to-png" 

A collection of lightweight Python utilities designed to generate pixel-perfect, 5cm-wide (receipt size) PNG images for thermal printers.

## 📂 Project Structure

```text
receipt-utils/
├── receipt_gen.py     # Program 1: Standard text & checklist formatter
├── calendar_gen.py    # Program 2: Monthly grid calendar generator
└── README.md          # Project documentation

```

---

## ⚙️ Setup & Installation

These scripts require Python 3 and the **Pillow (PIL)** library for image generation.

1. **Clone or create the directory:**
```bash
mkdir receipt-utils
cd receipt-utils

```


2. **Install the required dependencies:**
```bash
pip install Pillow

```



---

## 🛠️ Usage Guide

### 1. Text & Checklist Generator (`receipt_gen.py`)

Converts standard text files into receipt images. Features automatic text wrapping, custom alignment, and a dynamic checklist mode with hanging indents.

* **Standard centered text:**

```bash
  python receipt_gen.py -i shopping_list.txt -o receipt.png --align center

```

* **Checklist with checkboxes and custom margins:**

```bash
  python receipt_gen.py -i todo.txt -o checklist.png --checklist --margin 15

```

### 2. Monthly Calendar Generator (`calendar_gen.py`)

Generates a 5cm structured monthly calendar grid. Automatically defaults to the current month and year, with the ability to shade specific dates using a text file.

* **Quick current month calendar:**
```bash
python calendar_gen.py -o current_month.png

```


* **Specific month with highlighted dates (e.g., May 2026):**

```bash
  python calendar_gen.py -o marked_may.png -y 2026 -m 5 -i holidays.txt --greyscale 40

```

*(Note: The `holidays.txt` file should contain dates matching the `dd-mm-yyyy` format, one per line).*

---

## 📜 CLI Arguments Cheat Sheet

| Argument | Long Flag | Description | Default |
| --- | --- | --- | --- |
| `-i` | `--input` | Path to the input text file | *Required* |
| `-o` | `--output` | Path to save the output PNG file | *Required* |
| `-y` | `--year` | Year for calendar *(Calendar script only)* | Current Year |
| `-m` | `--month` | Month (1-12) for calendar *(Calendar script only)* | Current Month |
| `-a` | `--align` | Text alignment (`left`, `center`, `right`) | `left` |
| `-c` | `--checklist` | Enables checkbox layout *(Text script only)* | `False` |
| `--font-size` | — | Sets size of font rendering | `24` (text) / `22` (cal) |
| `--margin` | — | Margin padding in pixels | `10` (text) / `15` (cal) |
| `--greyscale` | — | Shading darkness % (0-100) *(Calendar script only)* | `50` |
| `--dpi` | — | Thermal printer output resolution adjustment | `203` |

---
