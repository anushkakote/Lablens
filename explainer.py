"""Plain-language explanations and chat answers built from evaluated findings."""
import re

import pandas as pd

from data_loader import build_alias_index
from evaluator import Finding, status_label, summarise
from llm import ask_llm, llm_available

DISCLAIMER = ("This tool explains values in simple words. It is not a diagnosis. "
              "Please discuss your results with a doctor.")

STATUS_ICON = {"normal": "🟢", "low": "🟠", "high": "🟠", "urgent-low": "🔴", "urgent-high": "🔴"}


def _fmt(x) -> str:
    if x is None:
        return "?"
    return f"{x:,.0f}" if float(x).is_integer() else f"{x:g}"


def range_text(f: Finding) -> str:
    if f.low is None and f.high is None:
        return "not available"
    return f"{_fmt(f.low)} - {_fmt(f.high)} {f.unit}".strip()


def value_text(f: Finding) -> str:
    return f"{f.qualifier}{_fmt(f.value)} {f.unit}".strip()


def findings_table(findings: list) -> pd.DataFrame:
    return pd.DataFrame([{
        "Test": f.name,
        "Your value": value_text(f),
        "Normal range": range_text(f),
        "Status": f"{STATUS_ICON[f.status]} {status_label(f)}",
        "Group": f.category,
    } for f in findings])


def explain_finding(f: Finding) -> str:
    lines = [
        f"**{f.name}: {value_text(f)}** ({status_label(f)}; range {range_text(f)})",
        f"- *What it is:* {f.what_it_is}",
        f"- *What this result can mean:* {f.meaning}",
    ]
    for n in f.notes:
        lines.append(f"- _{n}_")
    if f.status.startswith("urgent"):
        lines.append("- ⚠️ **This value is far outside the expected range. Please contact a doctor promptly.**")
    return "\n".join(lines)


def overall_summary(findings: list) -> str:
    if not findings:
        return "I could not find any recognised test values in this report."
    s = summarise(findings)
    parts = [f"I found **{s['total']}** recognised values. **{s['normal']}** are within range"
             f" and **{len(s['abnormal'])}** are outside it."]
    if s["urgent"]:
        names = ", ".join(f.name for f in s["urgent"])
        parts.append(f"🔴 **Needs prompt medical attention:** {names}.")
    if s["abnormal"]:
        parts.append("Out of range: " + ", ".join(
            f"{f.name} ({status_label(f).lower()})" for f in s["abnormal"]) + ".")
    else:
        parts.append("Everything I could read is in the normal range.")
    parts.append(DISCLAIMER)
    return "\n\n".join(parts)


def llm_context(findings: list) -> str:
    rows = []
    for f in findings:
        rows.append(f"- {f.name}: {value_text(f)}, range {range_text(f)}, status {status_label(f)}. "
                    f"What it is: {f.what_it_is} Meaning: {f.meaning}")
    return "\n".join(rows) or "No recognised values."


def _mentioned_keys(question: str, markers: pd.DataFrame) -> list:
    q = " " + re.sub(r"[^a-z0-9\+\-/ ]", " ", question.lower()) + " "
    keys = []
    for alias, key in build_alias_index(markers):
        if len(alias) <= 2:
            continue
        pat = " " + re.escape(alias) + " "
        if re.search(pat, q):
            q = re.sub(pat, " ", q, count=1)
            if key not in keys:
                keys.append(key)
    return keys


def answer(question: str, findings: list, markers: pd.DataFrame, history: list | None = None) -> str:
    ql = question.lower()
    by_key = {f.key: f for f in findings}
    keys = _mentioned_keys(question, markers)

    if keys:
        table = markers.set_index("Key")
        blocks = []
        for k in keys[:4]:
            if k in by_key:
                blocks.append(explain_finding(by_key[k]))
            else:
                r = table.loc[k]
                blocks.append(f"**{r['Name']}** is not in your uploaded report.\n- *What it is:* {r['What_It_Is']}"
                              f"\n- *If high:* {r['If_High']}\n- *If low:* {r['If_Low']}")
        return "\n\n".join(blocks) + "\n\n" + DISCLAIMER

    if re.search(r"abnormal|out of range|high|low|worr|problem|wrong|concern", ql) and findings:
        bad = [f for f in findings if f.status != "normal"]
        if not bad:
            return "Nothing I could read is outside the reference range.\n\n" + DISCLAIMER
        return "\n\n".join(explain_finding(f) for f in bad) + "\n\n" + DISCLAIMER

    if re.search(r"summar|overall|everything|all results|explain my report|explain it", ql):
        return overall_summary(findings)

    if llm_available() and findings:
        try:
            return ask_llm(question, llm_context(findings), history)
        except Exception as exc:  # network/key problems should not crash the chat
            return f"I couldn't reach the language model ({type(exc).__name__}). " \
                   "Try asking about a specific test, e.g. “What is hemoglobin?”"
    if not findings:
        return "Please upload or paste a lab report first, or ask about a test such as “What is TSH?”"
    return ("I can explain any test from your report. Try asking about one by name "
            "(e.g. “What does my ferritin mean?”) or ask for a summary. "
            "Add a Groq API key to enable open-ended questions.")
