"""Optional Groq-hosted language model, used only to phrase the answer.
All numbers and statuses come from evaluator.py; the model never decides them."""
import os

from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = (
    "You explain blood test results to a non-medical reader in simple, calm language. "
    "Use ONLY the results and marker notes supplied in the context. Do not diagnose, "
    "do not name specific medicines or doses, and do not invent values or ranges. "
    "If something is not in the context, say it is not in the report. "
    "Always remind the reader that a doctor should interpret the results. "
    "If any result is marked URGENT, tell the reader to contact a doctor promptly. "
    "Keep answers short, with plain words and no jargon."
)


def llm_available() -> bool:
    return bool(os.getenv("GROQ_API_KEY"))


def ask_llm(question: str, context: str, history: list | None = None) -> str:
    from groq import Groq
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for turn in (history or [])[-8:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({
        "role": "user",
        "content": f"Report context:\n{context}\n\nQuestion: {question}",
    })
    resp = client.chat.completions.create(model=model, messages=messages, temperature=0.2)
    return resp.choices[0].message.content.strip()
