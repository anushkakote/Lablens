"""One-off: align marker ranges with the cited sources and record where each range comes from.

Sources (read in full for this check):
  ABIM  = ABIM Laboratory Test Reference Ranges, revised January 2026
  ADA   = Standards of Care in Diabetes-2026, Section 2 (Diabetes Care 2026;49 Suppl 1:S27-S49)
  WHO   = Haemoglobin concentrations for the diagnosis of anaemia and assessment of severity (2011)
"""
from pathlib import Path

import pandas as pd

CSV = Path(__file__).parent / "markers.csv"
df = pd.read_csv(CSV, dtype=str).fillna("")

# key: (male_low, male_high, female_low, female_high, source)
ABIM = "ABIM Jan 2026"
NEW = {
    "hemoglobin": ("13", "18", "12", "16", "ABIM Jan 2026 (upper limits); WHO 2011 anaemia cut-offs (lower limits 13 / 12)"),
    "rbc": ("4.2", "5.9", "4.2", "5.9", ABIM),
    "hematocrit": ("42", "50", "37", "47", ABIM),
    "mcv": ("80", "98", "80", "98", ABIM),
    "mch": ("28", "32", "28", "32", ABIM),
    "mchc": ("33", "36", "33", "36", ABIM),
    "rdw": ("9.0", "14.5", "9.0", "14.5", ABIM),
    "wbc": ("4000", "11000", "4000", "11000", ABIM),
    "neutrophils": ("50", "75", "50", "75", "Derived from ABIM: segmented neutrophils 50-70 plus bands 0-5"),
    "lymphocytes": ("30", "45", "30", "45", ABIM),
    "eosinophils": ("0", "3", "0", "3", ABIM),
    "monocytes": ("0", "6", "0", "6", ABIM),
    "basophils": ("0", "1", "0", "1", ABIM),
    "platelets": ("150000", "450000", "150000", "450000", ABIM),
    "esr": ("0", "15", "0", "20", ABIM),
    "glucose_fasting": ("70", "99", "70", "99", "ABIM Jan 2026; ADA Standards 2026 (prediabetes 100-125, diabetes >=126)"),
    "glucose_pp": ("70", "139", "70", "139", "ADA Standards 2026 (2-h OGTT: <140 normal, 140-199 prediabetes, >=200 diabetes); applied to post-meal values as an approximation"),
    "glucose_random": ("70", "140", "70", "140", "Team-chosen; no reference-range source (ADA gives only the >=200 diagnostic value with symptoms)"),
    "hba1c": ("4.0", "5.6", "4.0", "5.6", "ABIM Jan 2026; ADA Standards 2026 (5.7-6.4 prediabetes, >=6.5 diabetes)"),
    "cholesterol_total": ("0", "199", "0", "199", "ABIM Jan 2026 (desirable <200)"),
    "ldl": ("0", "99", "0", "99", "ABIM Jan 2026 (optimal <100)"),
    "hdl": ("40", "100", "50", "100", "ABIM Jan 2026 (low: male <40, female <50); upper limit 100 team-chosen"),
    "triglycerides": ("0", "149", "0", "149", "ABIM Jan 2026 (normal <150)"),
    "vldl": ("2", "30", "2", "30", "Derived: Friedewald VLDL = triglycerides / 5, so normal triglycerides (<150) give <30; not listed by ABIM"),
    "creatinine": ("0.7", "1.3", "0.5", "1.1", ABIM),
    "urea": ("17", "43", "17", "43", "Derived from ABIM BUN 8-20 mg/dL x 2.14; urea itself is not listed by ABIM"),
    "bun": ("8", "20", "8", "20", ABIM),
    "uric_acid": ("3.0", "7.0", "3.0", "7.0", ABIM),
    "sodium": ("136", "145", "136", "145", ABIM),
    "potassium": ("3.5", "5.0", "3.5", "5.0", ABIM),
    "chloride": ("98", "106", "98", "106", ABIM),
    "calcium": ("8.6", "10.2", "8.6", "10.2", ABIM),
    "phosphorus": ("3.0", "4.5", "3.0", "4.5", ABIM),
    "magnesium": ("1.6", "2.6", "1.6", "2.6", ABIM),
    "bilirubin_total": ("0.3", "1.0", "0.3", "1.0", ABIM),
    "bilirubin_direct": ("0.1", "0.3", "0.1", "0.3", ABIM),
    "sgot": ("10", "40", "10", "40", ABIM),
    "sgpt": ("10", "40", "10", "40", ABIM),
    "alp": ("30", "120", "30", "120", ABIM),
    "ggt": ("9", "50", "8", "40", ABIM),
    "total_protein": ("5.5", "9.0", "5.5", "9.0", ABIM),
    "albumin": ("3.5", "5.5", "3.5", "5.5", ABIM),
    "globulin": ("2.0", "3.5", "2.0", "3.5", ABIM),
    "tsh": ("0.5", "4.0", "0.5", "4.0", ABIM),
    "t3": ("80", "180", "80", "180", ABIM),
    "t4": ("5", "12", "5", "12", ABIM),
    "ft4": ("0.8", "1.8", "0.8", "1.8", ABIM),
    "vitamin_d": ("30", "60", "30", "60", ABIM),
    "vitamin_b12": ("200", "800", "200", "800", ABIM),
    "folate": ("1.8", "9.0", "1.8", "9.0", ABIM),
    "ferritin": ("24", "336", "24", "307", ABIM),
    "iron": ("50", "150", "50", "150", ABIM),
    "tibc": ("250", "310", "250", "310", ABIM),
    "transferrin_sat": ("20", "50", "20", "50", ABIM),
    "crp": ("0", "8", "0", "8", "ABIM Jan 2026 (conventional CRP <=0.8 mg/dL = <=8 mg/L)"),
}
assert set(NEW) == set(df["Key"]), set(df["Key"]) ^ set(NEW)

df["Range_Source"] = ""
for key, (ml, mh, fl, fh, src) in NEW.items():
    i = df.index[df["Key"] == key][0]
    df.loc[i, ["Male_Low", "Male_High", "Female_Low", "Female_High", "Range_Source"]] = [ml, mh, fl, fh, src]

# Urgent thresholds are not published in the ABIM or ADA documents; say so in the source column.
has_crit = (df["Critical_Low"] != "") | (df["Critical_High"] != "")
df.loc[has_crit, "Range_Source"] += "; urgent thresholds team-chosen, not source-verified"

# Vitamin D wording: thresholds are the 2011 Endocrine Society ones, later revised.
i = df.index[df["Key"] == "vitamin_d"][0]
df.loc[i, "If_Low"] = ("Very common in India. The 2011 Endocrine Society guideline called below 20 ng/mL deficiency "
                       "and 21 to 29 insufficiency (a 2024 update moved away from fixed cut-offs). "
                       "Can cause bone pain and weakness.")
df.to_csv(CSV, index=False, encoding="utf-8", lineterminator="\n")
print(df.shape)
