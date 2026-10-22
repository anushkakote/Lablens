import sys
from pathlib import Path

import pymupdf
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data_loader import load_markers  # noqa: E402
from evaluator import evaluate  # noqa: E402
from explainer import answer, overall_summary  # noqa: E402
from extractor import extract_text  # noqa: E402
from report_parser import parse_report  # noqa: E402

SAMPLE = Path(__file__).resolve().parent.parent / "samples" / "sample_report.txt"
MARKERS = load_markers()


def run(text, sex="female"):
    return {f.key: f for f in evaluate(parse_report(text, MARKERS).values, MARKERS, sex)}


def test_marker_table_loads():
    assert len(MARKERS) >= 50
    assert MARKERS["Key"].is_unique


def test_every_marker_records_its_range_source_and_valid_ranges():
    assert (MARKERS["Range_Source"].str.strip() != "").all()
    assert (MARKERS["Male_Low"] < MARKERS["Male_High"]).all()
    assert (MARKERS["Female_Low"] < MARKERS["Female_High"]).all()


def test_ranges_follow_cited_source_values():
    # spot checks against ABIM Jan 2026 / ADA 2026
    f = run("Potassium 5.05 mmol/L\nAlkaline Phosphatase 125 U/L\nFasting Blood Sugar 100 mg/dL")
    assert f["potassium"].status == "high"
    assert f["alp"].status == "high"
    assert f["glucose_fasting"].status == "high"


def test_plain_pasted_values():
    f = run("Hb: 10.2 g/dL\nTSH 6.8 uIU/mL\nVitamin D 14 ng/mL")
    assert f["hemoglobin"].status == "low"
    assert f["tsh"].status == "high"
    assert f["vitamin_d"].status == "low"


def test_hba1c_not_confused_with_hemoglobin():
    f = run("HbA1c 5.9 %\nHemoglobin 13.5 g/dL")
    assert f["hba1c"].value == 5.9 and f["hba1c"].status == "high"
    assert f["hemoglobin"].value == 13.5 and f["hemoglobin"].status == "normal"


def test_sex_specific_range():
    assert run("Hemoglobin 16.5 g/dL", "female")["hemoglobin"].status == "high"
    assert run("Hemoglobin 16.5 g/dL", "male")["hemoglobin"].status == "normal"
    assert run("Hemoglobin 12.5 g/dL", "male")["hemoglobin"].status == "low"
    assert run("Hemoglobin 12.5 g/dL", "female")["hemoglobin"].status == "normal"


def test_report_range_takes_priority():
    f = run("Hemoglobin 11.0 g/dL 10.0 - 14.0")["hemoglobin"]
    assert f.status == "normal" and f.range_source == "report"


def test_urgent_value_flagged():
    assert run("Serum Potassium 6.8 mmol/L")["potassium"].status == "urgent-high"


def test_platelet_lakh_conversion():
    f = run("Platelet Count 2.1 lakh/cumm 1.5 - 4.1")["platelets"]
    assert f.value == 210000 and f.status == "normal"


def test_ratio_line_not_read_as_cholesterol():
    f = run("Total Cholesterol 190 mg/dL\nCholesterol/HDL Ratio 5.6")
    assert f["cholesterol_total"].value == 190


def test_unit_ending_in_L_is_kept_and_flag_column_ignored():
    f = run("Serum Potassium 4.1 mmol/L 3.5 - 5.1\nHemoglobin 10.2 L g/dL 12.0 - 15.0")
    assert f["potassium"].unit == "mmol/L"
    assert f["hemoglobin"].unit == "g/dL" and f["hemoglobin"].status == "low"


def test_aliases_with_brackets():
    f = run("SGOT (AST) 60 U/L 5 - 40")
    assert f["sgot"].status == "high"


def test_sample_report_end_to_end():
    result = parse_report(SAMPLE.read_text(), MARKERS)
    findings = evaluate(result.values, MARKERS, "female")
    assert len(findings) == 18  # 19 rows; the Cholesterol/HDL ratio row is deliberately skipped
    assert any("Ratio" in u for u in result.unrecognised)
    bad = {f.key for f in findings if f.status != "normal"}
    assert {"hemoglobin", "tsh", "vitamin_d", "ferritin", "potassium"} <= bad
    assert "rbc" not in bad and "creatinine" not in bad
    assert "URGENT" not in overall_summary(findings) or "Needs prompt" in overall_summary(findings)


def test_chat_marker_question():
    findings = list(run("Hemoglobin 10.2 g/dL").values())
    reply = answer("What does my low hemoglobin mean?", findings, MARKERS)
    assert "anaemia" in reply.lower()


def test_chat_marker_not_in_report():
    reply = answer("what is ferritin?", [], MARKERS)
    assert "not in your uploaded report" in reply


def _make_pdf(path):
    doc = pymupdf.open()
    page = doc.new_page()
    y = 80
    for name, val, unit, rng in [("Hemoglobin", "10.2", "g/dL", "12.0 - 15.0"),
                                 ("TSH", "6.8", "uIU/mL", "0.4 - 4.0"),
                                 ("Creatinine", "0.8", "mg/dL", "0.6 - 1.1")]:
        for x, t in ((50, name), (200, val), (260, unit), (360, rng)):
            page.insert_text((x, y), t, fontsize=11)
        y += 22
    doc.save(path)
    return doc


def test_pdf_table_rows_reassembled(tmp_path):
    p = tmp_path / "r.pdf"
    _make_pdf(str(p))
    text, method = extract_text(p.read_bytes(), "r.pdf")
    assert method == "pdf-text"
    f = run(text)
    assert f["hemoglobin"].value == 10.2 and f["tsh"].status == "high"


def test_scanned_image_ocr(tmp_path):
    pytest.importorskip("rapidocr_onnxruntime")
    p = tmp_path / "r.pdf"
    doc = _make_pdf(str(p))
    png = doc[0].get_pixmap(dpi=200).tobytes("png")
    text, method = extract_text(png, "scan.png")
    assert method == "image-ocr"
    f = run(text)
    assert f["hemoglobin"].status == "low"
    assert f["tsh"].status == "high"
