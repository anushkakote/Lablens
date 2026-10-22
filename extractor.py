"""Gets text out of PDFs and photos, rebuilding table rows so that
'Hemoglobin   10.2   g/dL   12.0 - 15.0' stays on a single line."""
import io
import statistics

import pymupdf
from PIL import Image

_ocr_engine = None


def _group_rows(items: list) -> str:
    """items: (x0, y0, x1, y1, text). Cluster by vertical centre into rows."""
    if not items:
        return ""
    heights = [max(i[3] - i[1], 1) for i in items]
    tol = statistics.median(heights) * 0.6
    items = sorted(items, key=lambda i: (i[1] + i[3]) / 2)
    rows, current, cur_y = [], [], None
    for it in items:
        yc = (it[1] + it[3]) / 2
        if cur_y is None or abs(yc - cur_y) <= tol:
            current.append(it)
            cur_y = yc if cur_y is None else (cur_y + yc) / 2
        else:
            rows.append(current)
            current, cur_y = [it], yc
    rows.append(current)
    return "\n".join("  ".join(t[4] for t in sorted(r, key=lambda i: i[0])) for r in rows)


def _get_ocr():
    global _ocr_engine
    if _ocr_engine is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr_engine = RapidOCR()
    return _ocr_engine


def ocr_image(image: Image.Image) -> str:
    import numpy as np
    engine = _get_ocr()
    result, _ = engine(np.array(image.convert("RGB")))
    if not result:
        return ""
    items = []
    for box, text, _conf in result:
        xs = [p[0] for p in box]
        ys = [p[1] for p in box]
        items.append((min(xs), min(ys), max(xs), max(ys), text))
    return _group_rows(items)


def _pdf_text(doc: "pymupdf.Document") -> str:
    pages = []
    for page in doc:
        words = [(w[0], w[1], w[2], w[3], w[4]) for w in page.get_text("words")]
        pages.append(_group_rows(words))
    return "\n".join(pages)


def _pdf_ocr(doc: "pymupdf.Document") -> str:
    out = []
    for page in doc:
        pix = page.get_pixmap(dpi=200)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        out.append(ocr_image(img))
    return "\n".join(out)


def extract_text(data: bytes, filename: str) -> tuple[str, str]:
    """Returns (text, method) where method is 'pdf-text', 'pdf-ocr', 'image-ocr' or 'plain'."""
    name = filename.lower()
    if name.endswith(".pdf"):
        doc = pymupdf.open(stream=data, filetype="pdf")
        text = _pdf_text(doc)
        if len(text.strip()) >= 40:
            return text, "pdf-text"
        return _pdf_ocr(doc), "pdf-ocr"
    if name.endswith((".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff")):
        return ocr_image(Image.open(io.BytesIO(data))), "image-ocr"
    return data.decode("utf-8", errors="replace"), "plain"
