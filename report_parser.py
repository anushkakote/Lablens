"""Turns raw report text into structured (marker, value, unit, range) rows."""
import re
from dataclasses import dataclass, field
from typing import Optional

import pandas as pd

from data_loader import build_alias_index

NUM = r"[<>]?\s?\d[\d,]*(?:\.\d+)?"
NUM_RE = re.compile(NUM)
RANGE_RE = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(?:-|–|—|to)\s*(\d[\d,]*(?:\.\d+)?)")
UNIT_RE = re.compile(
    r"^\s*((?:x\s?10\^?[0-9]+\s?/\s?\S+)|(?:[a-zA-Zµμ%/\^\d\.\*]+(?:/[a-zA-Zµμ%\d\.\*]+)*))"
)
LEADING_NOISE = re.compile(r"^[\s\W\d]*?(?=[A-Za-z])")  # serial numbers, bullets
SKIP_WORDS = ("reference", "method", "page ", "patient", "collected", "reported",
              "sample", "lab no", "age", "ref. range", "test name")


@dataclass
class ParsedValue:
    key: str
    value: float
    unit: str
    ref_low: Optional[float]
    ref_high: Optional[float]
    raw_line: str
    qualifier: str = ""  # '<' or '>' if the report said e.g. '<5'
    notes: list = field(default_factory=list)


@dataclass
class ParseResult:
    values: list
    unrecognised: list


def _to_float(s: str) -> float:
    return float(s.replace(",", "").replace("<", "").replace(">", "").strip())


def _fix_scale(key: str, value: float, unit: str, notes: list) -> tuple[float, str]:
    """Labs print counts in different scales. Bring them to cells/uL."""
    u = unit.lower().replace(" ", "")
    if key == "platelets":
        if "lakh" in u or (value < 20 and "10" not in u):
            notes.append("Converted from lakhs to cells/uL.")
            return value * 100000, "cells/uL"
        if value < 1000:
            notes.append("Converted from thousands to cells/uL.")
            return value * 1000, "cells/uL"
    if key == "wbc" and value < 100:
        notes.append("Converted from thousands to cells/uL.")
        return value * 1000, "cells/uL"
    if key == "rbc" and value > 100:
        notes.append("Converted to million/uL.")
        return value / 1_000_000, "million/uL"
    return value, unit


def _normalise_unit(unit: str) -> str:
    unit = unit.strip().strip(".,;")
    return unit.replace("µ", "u").replace("μ", "u")


def parse_report(text: str, markers: pd.DataFrame) -> ParseResult:
    aliases = build_alias_index(markers)
    alias_regexes = [
        (re.compile(r"^" + re.escape(a).replace(r"\ ", r"\s+") + r"(?![A-Za-z0-9])", re.I), k)
        for a, k in aliases
    ]
    found: dict = {}
    unrecognised: list = []

    for raw in text.splitlines():
        line = raw.strip()
        if len(line) < 3:
            continue
        low = line.lower()
        if any(low.startswith(w) for w in SKIP_WORDS):
            continue
        body = LEADING_NOISE.sub("", line, count=1)
        matched = None
        for rx, key in alias_regexes:
            m = rx.match(body)
            if m:
                matched = (key, body[m.end():])
                break
        if not matched:
            if re.search(r"[A-Za-z]{3,}", body) and NUM_RE.search(body) and len(body) < 90 \
                    and not re.search(r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}", body):
                unrecognised.append(line)
            continue

        key, rest = matched
        if re.match(r"\s*(/|ratio|index)", rest, re.I):  # e.g. 'Cholesterol/HDL ratio'
            unrecognised.append(line)
            continue
        rest = re.sub(r"^\s*(\([^)]*\)\s*)+", " ", rest)      # '(AST)' style tags
        rest = re.sub(r"^[\s:\-–—\.]+", "", rest)
        num_m = NUM_RE.match(rest) or NUM_RE.search(rest)
        if not num_m:
            continue
        qualifier = ""
        token = num_m.group(0)
        if token.strip()[0] in "<>":
            qualifier = token.strip()[0]
        try:
            value = _to_float(token)
        except ValueError:
            continue
        after = rest[num_m.end():]
        after = re.sub(r"(?<=\s)(H|L|HIGH|LOW|High|Low)(?=\s|$)", " ", after)  # flag column, not 'mmol/L'
        range_m = RANGE_RE.search(after)
        unit_text = after[: range_m.start()] if range_m else after
        unit_m = UNIT_RE.match(unit_text)
        unit = _normalise_unit(unit_m.group(1)) if unit_m else ""
        if unit and re.fullmatch(r"[\d\.\-]+", unit):
            unit = ""
        ref_low = ref_high = None
        if range_m:
            ref_low, ref_high = _to_float(range_m.group(1)), _to_float(range_m.group(2))
            if ref_low >= ref_high:
                ref_low = ref_high = None
        notes: list = []
        value, unit = _fix_scale(key, value, unit, notes)
        if ref_low is not None and ref_high is not None:
            if key == "platelets" and ref_high < 20:
                ref_low, ref_high = ref_low * 100000, ref_high * 100000
            elif key in ("platelets", "wbc") and ref_high < 1000:
                ref_low, ref_high = ref_low * 1000, ref_high * 1000
        # keep the first reading of each marker (later lines are often repeats)
        if key not in found:
            found[key] = ParsedValue(key, value, unit, ref_low, ref_high, line, qualifier, notes)

    return ParseResult(values=list(found.values()), unrecognised=unrecognised)
