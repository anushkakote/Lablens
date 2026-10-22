"""Renders the two corpus figures from the real files: the raw sample report and the reference table."""
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = r"C:\Users\user\Desktop\Lab Report Explainer"
mono = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 22)
reg = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 20)
bold = ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf", 19)

# ---- Figure: raw, unannotated input (sample report) ----
lines = open(ROOT + r"\samples\sample_report.txt", encoding="utf8").read().splitlines()
pad, lh = 30, 32
w = 1100
h = pad * 2 + lh * len(lines)
img = Image.new("RGB", (w, h), "white")
d = ImageDraw.Draw(img)
d.rectangle([0, 0, w - 1, h - 1], outline="black", width=2)
for i, ln in enumerate(lines):
    d.text((pad, pad + i * lh), ln, font=mono, fill="black")
img.save(ROOT + r"\report\fig_raw_sample_report.png")

# ---- Figure: annotated reference table (first rows of markers.csv) ----
df = pd.read_csv(ROOT + r"\data\markers.csv", dtype=str).fillna("")
cols = ["Key", "Category", "Unit", "Male_Low", "Male_High", "Female_Low", "Female_High", "Critical_Low", "Critical_High", "Aliases"]
sub = df.head(9)[cols].copy()
sub["Aliases"] = sub["Aliases"].str.slice(0, 26) + "..."
widths = [140, 135, 125, 140, 140, 150, 150, 160, 160, 300]
rh = 40
w = sum(widths) + 2
h = rh * (len(sub) + 1) + 2
img = Image.new("RGB", (w, h), "white")
d = ImageDraw.Draw(img)
x = 1
for c, cw in zip(cols, widths):
    d.rectangle([x, 1, x + cw, 1 + rh], outline="black", width=1)
    d.text((x + 8, 1 + rh / 2), c, font=bold, fill="black", anchor="lm")
    x += cw
for r, (_, row) in enumerate(sub.iterrows(), start=1):
    x = 1
    for c, cw in zip(cols, widths):
        d.rectangle([x, 1 + r * rh, x + cw, 1 + (r + 1) * rh], outline="black", width=1)
        d.text((x + 8, 1 + r * rh + rh / 2), str(row[c]), font=reg, fill="black", anchor="lm")
        x += cw
img.save(ROOT + r"\report\fig_reference_table.png")
print("ok", img.size)
