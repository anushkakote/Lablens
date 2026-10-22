"""Draws the system architecture figure used in the report."""
from PIL import Image, ImageDraw, ImageFont

W, H = 1500, 1000
img = Image.new("RGB", (W, H), "white")
d = ImageDraw.Draw(img)
bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 30)
reg = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 24)
title = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 40)

GREEN, BORDER, ORANGE = (255, 255, 255), (0, 0, 0), (0, 0, 0)  # black and white only
INK = (0, 0, 0)


def box(x, y, w, h, head, lines, fill=GREEN):
    d.rounded_rectangle([x, y, x + w, y + h], 18, fill=fill, outline=BORDER, width=4)
    d.text((x + w / 2, y + 34), head, font=bold, fill=INK, anchor="mm")
    for i, ln in enumerate(lines):
        d.text((x + w / 2, y + 78 + i * 32), ln, font=reg, fill=INK, anchor="mm")


def arrow(x1, y1, x2, y2):
    d.line([x1, y1, x2, y2], fill=ORANGE, width=5)
    if y2 != y1:
        d.polygon([(x2, y2), (x2 - 14, y2 - 24), (x2 + 14, y2 - 24)], fill=ORANGE)
    else:
        d.polygon([(x2, y2), (x2 - 24, y2 - 14), (x2 - 24, y2 + 14)], fill=ORANGE)


d.text((W / 2 - 150, 45), "LabLens - System Architecture", font=title, fill=INK, anchor="mm")
cx, bw = 520, 560
box(cx, 100, bw, 130, "User / Chat Interface", ["Streamlit app: upload PDF or photo,", "or paste values; chat about results"])
box(cx, 290, bw, 130, "Text Extraction", ["PDF text layer, or RapidOCR for photos", "and scanned PDFs; rows rebuilt by position"])
box(cx, 480, bw, 130, "Parsing", ["Alias matching, value, unit and printed", "range; unit scaling (lakh, thousands)"])
box(cx, 670, bw, 130, "Evaluation", ["Low / normal / high / urgent, severity,", "sex-specific ranges"])
box(cx - 400, 860, bw - 40, 110, "Rule-based Explanations", ["Table, explanations, chat answers"])
box(cx + 340, 860, bw - 40, 110, "Optional Groq LLM", ["Phrasing of open-ended questions"])
for y1, y2 in ((230, 290), (420, 480), (610, 670)):
    arrow(cx + bw / 2, y1, cx + bw / 2, y2)
arrow(cx + 120, 800, cx - 120, 860)
arrow(cx + bw - 120, 800, cx + bw + 120, 860)
box(60, 480, 340, 190, "Marker Reference", ["data/markers.csv", "55 markers, 248 aliases,", "ranges and plain text"], fill=(255, 255, 255))
arrow(400, 560, cx, 560)
img.save(r"C:\Users\user\Desktop\Lab Report Explainer\report\architecture.png")
