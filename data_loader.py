"""Loads the marker reference table (aliases, ranges, plain-language text)."""
from pathlib import Path

import pandas as pd

DATA_PATH = Path(__file__).parent / "data" / "markers.csv"

NUMERIC_COLS = [
    "Male_Low", "Male_High", "Female_Low", "Female_High",
    "Critical_Low", "Critical_High",
]


def load_markers(path: Path = DATA_PATH) -> pd.DataFrame:
    if not Path(path).exists():
        raise FileNotFoundError(f"Marker reference file not found: {path}")
    df = pd.read_csv(path, dtype=str).fillna("")
    for col in NUMERIC_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def build_alias_index(df: pd.DataFrame) -> list[tuple[str, str]]:
    """Return (alias, marker_key) pairs, longest alias first so that
    'hemoglobin a1c' is tried before 'hemoglobin'."""
    pairs = []
    for _, row in df.iterrows():
        aliases = {a.strip().lower() for a in row["Aliases"].split("|") if a.strip()}
        aliases.add(row["Name"].lower())
        for alias in aliases:
            pairs.append((alias, row["Key"]))
    pairs.sort(key=lambda p: len(p[0]), reverse=True)
    return pairs
