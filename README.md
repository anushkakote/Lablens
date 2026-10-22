# LabLens: blood report explainer chatbot

Upload a lab report (PDF or photo) or paste values. LabLens reads each test, compares it with the
reference range, flags anything out of range and explains it in plain language. You can then chat
about your results.

## Run
```
pip install -r requirements.txt
streamlit run app.py
```
Optional: copy `.env.example` to `.env` and add a Groq API key for open-ended questions.

## Pipeline
1. `extractor.py`: PDF text, or OCR (RapidOCR) for photos and scanned PDFs. Table rows are rebuilt by position.
2. `report_parser.py`: alias matching, value / unit / printed range extraction, unit scaling.
3. `evaluator.py`: low / normal / high / urgent, severity, sex-specific ranges.
4. `explainer.py`: deterministic plain-language text and chat routing; `llm.py` adds optional Groq answers.
5. `data/markers.csv`: 55 markers with aliases, ranges and explanations (the factual source). The
   `Range_Source` column records where each range comes from: ABIM Laboratory Test Reference Ranges
   (January 2026), ADA Standards of Care 2026, WHO 2011 (haemoglobin lower limits), or "team-chosen".
   Urgent thresholds and the plain-language explanations are the team's own and have not been clinically reviewed.

## Tests
```
python -m pytest tests -q
```

This tool is educational and is not a diagnosis.
