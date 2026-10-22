"""Compares parsed values with reference ranges and assigns a status."""
from dataclasses import dataclass
from typing import Optional

import pandas as pd

from report_parser import ParsedValue

SEVERITY_LABELS = {0: "", 1: "slightly", 2: "moderately", 3: "markedly"}


@dataclass
class Finding:
    key: str
    name: str
    category: str
    value: float
    unit: str
    qualifier: str
    low: Optional[float]
    high: Optional[float]
    range_source: str       # 'report' or 'standard'
    status: str             # low | normal | high | urgent-low | urgent-high
    severity: int           # 0..3
    what_it_is: str
    meaning: str
    notes: list


def _severity(value: float, low: Optional[float], high: Optional[float]) -> int:
    if high is not None and value > high and high > 0:
        gap = (value - high) / high
    elif low is not None and value < low and low > 0:
        gap = (low - value) / low
    else:
        return 0
    if gap <= 0.10:
        return 1
    if gap <= 0.30:
        return 2
    return 3


def _num(x) -> Optional[float]:
    return None if pd.isna(x) else float(x)


def evaluate(parsed: list, markers: pd.DataFrame, sex: str = "unknown") -> list:
    """sex: 'male', 'female' or 'unknown' (unknown uses the widest combined range)."""
    table = markers.set_index("Key")
    findings = []
    for p in parsed:
        row = table.loc[p.key]
        m_lo, m_hi = _num(row["Male_Low"]), _num(row["Male_High"])
        f_lo, f_hi = _num(row["Female_Low"]), _num(row["Female_High"])
        if sex == "male":
            std_lo, std_hi = m_lo, m_hi
        elif sex == "female":
            std_lo, std_hi = f_lo, f_hi
        else:
            std_lo = min(x for x in (m_lo, f_lo) if x is not None)
            std_hi = max(x for x in (m_hi, f_hi) if x is not None)

        if p.ref_low is not None and p.ref_high is not None:
            lo, hi, src = p.ref_low, p.ref_high, "report"
        else:
            lo, hi, src = std_lo, std_hi, "standard"

        crit_lo, crit_hi = _num(row["Critical_Low"]), _num(row["Critical_High"])
        v = p.value
        if crit_lo is not None and v < crit_lo:
            status, sev = "urgent-low", 3
        elif crit_hi is not None and v > crit_hi:
            status, sev = "urgent-high", 3
        elif lo is not None and v < lo and p.qualifier != "<":
            status, sev = "low", _severity(v, lo, hi)
        elif hi is not None and ((v > hi and p.qualifier != ">") or (p.qualifier == ">" and v >= hi)):
            status, sev = "high", _severity(v, lo, hi)
        else:
            status, sev = "normal", 0

        if status == "normal":
            meaning = "Within the reference range."
        elif status in ("high", "urgent-high"):
            meaning = row["If_High"]
        else:
            meaning = row["If_Low"]

        notes = list(p.notes)
        if src == "report":
            notes.append("Judged against the range printed on your report.")
        sex_specific = (m_lo, m_hi) != (f_lo, f_hi)
        if sex == "unknown" and sex_specific and src == "standard":
            notes.append("Sex not given, so a combined male/female range was used.")
        findings.append(Finding(
            key=p.key, name=row["Name"], category=row["Category"], value=v,
            unit=p.unit or row["Unit"], qualifier=p.qualifier, low=lo, high=hi,
            range_source=src, status=status, severity=sev,
            what_it_is=row["What_It_Is"], meaning=meaning, notes=notes,
        ))
    return findings


def status_label(f: Finding) -> str:
    if f.status == "normal":
        return "Normal"
    if f.status.startswith("urgent"):
        return "URGENT " + ("high" if f.status.endswith("high") else "low")
    adj = SEVERITY_LABELS.get(f.severity, "")
    return f"{adj} {f.status}".strip().capitalize()


def summarise(findings: list) -> dict:
    out = [f for f in findings if f.status != "normal"]
    return {
        "total": len(findings),
        "normal": len(findings) - len(out),
        "abnormal": out,
        "urgent": [f for f in findings if f.status.startswith("urgent")],
    }
