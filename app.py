"""LabLens: a chatbot that explains blood test reports in plain language."""
import streamlit as st

from data_loader import load_markers
from evaluator import evaluate, status_label
from explainer import (DISCLAIMER, STATUS_ICON, answer, explain_finding,
                       findings_table, overall_summary)
from extractor import extract_text
from llm import llm_available
from report_parser import parse_report

st.set_page_config(page_title="LabLens", page_icon="🧪", layout="wide")


@st.cache_data
def get_markers():
    return load_markers()


markers = get_markers()

for key, default in (("messages", []), ("findings", []), ("unrecognised", []),
                     ("raw_text", ""), ("method", "")):
    st.session_state.setdefault(key, default)


def process(text: str, method: str, sex: str):
    result = parse_report(text, markers)
    st.session_state.findings = evaluate(result.values, markers, sex)
    st.session_state.unrecognised = result.unrecognised
    st.session_state.raw_text = text
    st.session_state.method = method
    st.session_state.messages = [{"role": "assistant",
                                  "content": overall_summary(st.session_state.findings)}]


with st.sidebar:
    st.title("🧪 LabLens")
    st.caption("Your blood report, in plain words.")
    sex = st.radio("Sex (changes some normal ranges)", ["unknown", "female", "male"], horizontal=True)
    upload = st.file_uploader("Upload report (PDF or photo)", type=["pdf", "png", "jpg", "jpeg", "webp"])
    pasted = st.text_area("…or paste values", height=140,
                          placeholder="Hemoglobin 10.2 g/dL\nTSH 6.8 uIU/mL\nVitamin D 14 ng/mL")
    if st.button("Explain my report", type="primary", use_container_width=True):
        try:
            if upload is not None:
                with st.spinner("Reading your report…"):
                    text, method = extract_text(upload.getvalue(), upload.name)
            elif pasted.strip():
                text, method = pasted, "plain"
            else:
                st.warning("Upload a file or paste some values first.")
                st.stop()
            process(text, method, sex)
        except Exception as exc:
            st.error(f"Could not read that file ({type(exc).__name__}: {exc}).")
    if st.button("New report", use_container_width=True):
        for k in ("messages", "findings", "unrecognised"):
            st.session_state[k] = []
        st.session_state.raw_text = ""
        st.rerun()
    st.divider()
    st.caption("🔑 Language model: " + ("on (Groq)" if llm_available() else "off (rule-based answers only)"))
    st.info(DISCLAIMER)

st.header("LabLens")
st.caption("Upload a blood test report. Get each result explained, with anything out of range flagged.")

findings = st.session_state.findings
if findings:
    n_bad = sum(f.status != "normal" for f in findings)
    c1, c2, c3 = st.columns(3)
    c1.metric("Values read", len(findings))
    c2.metric("In range", len(findings) - n_bad)
    c3.metric("Out of range", n_bad)

    tab_tbl, tab_detail, tab_raw = st.tabs(["Results table", "Explanations", "What I read"])
    with tab_tbl:
        df = findings_table(findings)
        st.dataframe(df, use_container_width=True, hide_index=True)
        if st.session_state.unrecognised:
            with st.expander(f"{len(st.session_state.unrecognised)} lines I could not match to a known test"):
                for line in st.session_state.unrecognised:
                    st.text(line)
    with tab_detail:
        only_bad = st.toggle("Show only out-of-range", value=True)
        for f in findings:
            if only_bad and f.status == "normal":
                continue
            with st.container(border=True):
                st.markdown(f"{STATUS_ICON[f.status]} " + explain_finding(f))
    with tab_raw:
        st.caption(f"Extraction method: {st.session_state.method}. Check this against your report.")
        st.code(st.session_state.raw_text or "(nothing)")
elif st.session_state.raw_text:
    st.warning("I read the file but couldn't match any known tests. Check the 'What I read' text or paste the values.")
    st.code(st.session_state.raw_text)

st.subheader("Ask about your results")
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if prompt := st.chat_input("e.g. What does my low hemoglobin mean?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    reply = answer(prompt, st.session_state.findings, markers, st.session_state.messages[:-1])
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.rerun()
