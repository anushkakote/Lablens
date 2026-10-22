// Builds LabLens_CCA3_Report.docx. Run: node build_report.js (needs the `docx` package on NODE_PATH)
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun, Footer,
  AlignmentType, LevelFormat, WidthType, BorderStyle, ShadingType, PageNumber, PageBreak,
  HeadingLevel, ExternalHyperlink,
} = require("docx");

const FONT = "Times New Roman";
const W = 9638; // content width (A4, 2 cm margins)

// ---- inline markup: **bold**, `code`, _italic_ ----
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|`[^`]+`)/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const tok = m[0];
    if (tok.startsWith("**")) out.push(new TextRun({ text: tok.slice(2, -2), bold: true, font: FONT, ...base }));
    else out.push(new TextRun({ text: tok.slice(1, -1), font: "Courier New", size: 20, ...base }));
    last = m.index + tok.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}
const P = (text, opts = {}) => new Paragraph({
  children: runs(text, opts.run || {}), alignment: opts.align || AlignmentType.JUSTIFIED,
  spacing: { after: opts.after ?? 120, line: 276 }, keepNext: opts.keepNext,
});
// reference line whose trailing URL becomes a clickable link (black, underlined)
const refP = (text) => {
  const m = text.match(/^(.*?)(https?:\/\/\S+)$/);
  return new Paragraph({
    alignment: AlignmentType.LEFT, spacing: { after: 120, line: 276 },
    children: [
      ...runs(m[1]),
      new ExternalHyperlink({ link: m[2], children: [new TextRun({ text: m[2], font: FONT, underline: {} })] }),
    ],
  });
};
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, bold: true, font: FONT, size: 30 })], spacing: { before: 240, after: 120 }, keepNext: true });
const H2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, bold: true, font: FONT, size: 25 })], spacing: { before: 200, after: 100 }, keepNext: true });
const H3 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_3, children: [new TextRun({ text: t, bold: true, font: FONT, size: 22 })], spacing: { before: 140, after: 80 }, keepNext: true });
const B = (t) => new Paragraph({ numbering: { reference: "bul", level: 0 }, children: runs(t), spacing: { after: 70, line: 264 }, alignment: AlignmentType.JUSTIFIED });
const CAP = (t) => new Paragraph({ children: [new TextRun({ text: t, italics: true, font: FONT, size: 20 })], alignment: AlignmentType.CENTER, spacing: { after: 160 } });
const PH = (t) => new Paragraph({
  children: [new TextRun({ text: t, italics: true, font: FONT, size: 20, color: "000000" })],
  alignment: AlignmentType.CENTER, spacing: { before: 60, after: 160 },
  border: { top: dash(), bottom: dash(), left: dash(), right: dash() },
});
function dash() { return { style: BorderStyle.DASHED, size: 6, color: "000000", space: 6 }; }
const BLUE = "0070C0"; // used only for table header titles

const thin = { style: BorderStyle.SINGLE, size: 4, color: "000000" };
const borders = { top: thin, bottom: thin, left: thin, right: thin };
function table(widths, rows, header = true) {
  return new Table({
    width: { size: W, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: header && ri === 0, cantSplit: true,
      children: r.map((c, ci) => new TableCell({
        width: { size: widths[ci], type: WidthType.DXA }, borders,
        margins: { top: 60, bottom: 60, left: 100, right: 100 },
        children: [new Paragraph({ children: runs(c, header && ri === 0 ? { bold: true, size: 21 } : { size: 21 }), alignment: AlignmentType.LEFT })],
      })),
    })),
  });
}
const gap = () => new Paragraph({ children: [], spacing: { after: 120 } });
const img = (file, w, h) => new Paragraph({
  alignment: AlignmentType.CENTER, spacing: { before: 80, after: 60 }, keepNext: true,
  children: [new ImageRun({ type: path.extname(file).slice(1).replace("jpg", "jpg"), data: fs.readFileSync(path.join(__dirname, file)), transformation: { width: w, height: h }, altText: { title: file, description: file, name: file } })],
});

// ================= COVER =================
const cover = [
  new Paragraph({ children: [], spacing: { before: 800 } }),
  img("logo.jpg", 480, 127),
  new Paragraph({ children: [], spacing: { before: 700 } }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "CCNLP - CCA3 REPORT", bold: true, underline: {}, font: FONT, size: 30 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: "GROUP NO- [Group No.]", bold: true, font: FONT, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [new TextRun({ text: "PANEL- [Panel]", bold: true, font: FONT, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 240 }, children: [
    new TextRun({ text: "TOPIC: ", bold: true, font: FONT, size: 24 }),
    new TextRun({ text: "LabLens - Chatbot for plain-language explanation of blood test reports", bold: true, font: FONT, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [
    new TextRun({ text: "Submitted to: ", font: FONT, size: 24 }), new TextRun({ text: "Dr. Suja Panickar", bold: true, font: FONT, size: 24 })] }),
  table([900, 5000, 3738], [["Sr.no", "Name", "PRN"], ["1", "Anushka Kote", "1032233621"]]),
  new Paragraph({ children: [new PageBreak()] }),
];

// ================= BODY =================
const body = [
  H1("Problem Statement"),
  P("Blood test reports are handed to patients as tables of abbreviations, numbers, units and reference ranges. A reader has to work out what each marker means, whether the value is inside the range, and how far outside it is. Reports from different laboratories use different layouts, units (for example platelets in lakh/cumm or in thousands/uL) and range conventions, and they are often shared as PDFs or phone photos. Many people therefore leave a consultation without understanding their own results."),
  P("LabLens addresses this with a chatbot. The user uploads a report as a PDF or a photo, or pastes the values. The application reads each recognised test, compares the value with a reference range, flags values that are low, high or urgent, and explains every marker in plain language. The user can then ask follow-up questions in a chat. All values, ranges and statuses are produced by deterministic code from a supplied reference table; a language model is optional and is used only to phrase answers to open-ended questions. LabLens is an educational tool and does not give a diagnosis."),

  H1("Objectives"),
  table([2300, 2700, 2300, 2338], [
    ["Objective", "Technical Objective", "Models / Tools", "Expected Output"],
    ["1. Read lab reports in common formats.", "Extract text from PDFs, scanned PDFs and photos; rebuild table rows; locate each test, value, unit and printed range.", "PyMuPDF, RapidOCR (ONNX), Pillow, regular expressions, Pandas.", "A structured list of recognised tests with value, unit and range; unmatched lines listed separately."],
    ["2. Flag out-of-range results.", "Compare each value with the range printed on the report, or with a stored sex-specific range; grade severity; detect urgent values.", "Python rule logic, marker reference CSV.", "Each result labelled normal, slightly / moderately / markedly low or high, or URGENT."],
    ["3. Explain results and answer questions in plain language.", "Generate explanations from the reference table; route chat questions to the right marker; optionally pass results to a language model.", "Streamlit, rule-based answer routing, Groq API (optional).", "A results table, per-test explanations, an overall summary and a chat that stays tied to the report."],
  ]),

  H1("Model / Tool Used and Its Purpose"),
  table([3200, 6438], [
    ["Sr. No.", "Purpose"],
    ["1. Streamlit", "Builds the browser-based interface: sidebar for upload / paste / sex selection, results table, explanation tabs, chat."],
    ["2. Python", "Connects the modules: extraction, parsing, evaluation, explanation and chat routing."],
    ["3. Pandas", "Loads `data/markers.csv`, converts range columns to numbers and builds the results table."],
    ["4. PyMuPDF", "Reads the text layer of PDFs word by word with coordinates, and renders scanned PDF pages to images for OCR."],
    ["5. RapidOCR (ONNX Runtime)", "Optical character recognition for photos and scanned pages. It runs locally and needs no separate OCR program."],
    ["6. Pillow", "Opens and converts uploaded images before OCR."],
    ["7. Groq API (optional)", "If a key is configured, phrases answers to open-ended questions from the evaluated results. The default model name in the code is `llama-3.3-70b-versatile`, configurable through `GROQ_MODEL`."],
    ["8. python-dotenv", "Loads the API key and model name from a `.env` file."],
    ["9. pytest", "Runs the project's automated checks."],
  ]),

  H1("1. Abstract"),
  P("LabLens is a blood-report explainer built in Python with a Streamlit interface. A user uploads a PDF or photo of a lab report, or pastes values. Text is taken from the PDF text layer or by RapidOCR, and table rows are rebuilt from word positions. A parser matches each line to one of 55 markers using 248 alias names, extracts the value, unit and printed reference range, and corrects common scale differences. An evaluator then labels each result low, normal, high or urgent with a severity grade, using the range printed on the report when present and a stored male / female range otherwise. Explanations come from a reference table written for the project; chat questions about a specific test are answered directly from that table, while open-ended questions can optionally go to a Groq-hosted model."),
  P("The reference table has 55 rows and 15 columns, and each marker's range records its source. The repository contains 17 automated tests, all of which passed in the final run. A demonstration run on nine pasted values recognised all nine, flagged eight as out of range and marked a potassium of 6.8 mmol/L as urgent. The system's main limitations are that the urgent thresholds and explanations have not been clinically reviewed (the ranges themselves were checked against ABIM 2026 and ADA 2026), that accuracy on real reports has not been measured, and that the optional language-model path has not been exercised."),

  H1("2. Introduction"),
  P("A blood test report packs a lot of information into a small space, but it is written for clinicians. Patients commonly want to know three things: which results are outside the normal range, how serious that is, and what the test actually measures. Answering these by hand means searching for each abbreviation, finding the right range for the patient's sex, and converting units when the laboratory uses an unusual scale."),
  P("LabLens brings these steps into one conversational tool. It first turns the uploaded file into text, then into structured values, then compares those values with reference ranges, and finally explains the result in everyday words. The design keeps every number and every status under deterministic control: a language model is never asked to decide whether a value is high or low, only (optionally) to phrase an answer from results that the code has already evaluated."),

  H2("2.1 Research Questions"),
  B("**RQ1** - How can a chatbot make blood test results understandable to a non-medical reader while keeping every value and status accurate?"),
  B("**RQ2** - How can text extraction, alias matching and unit handling turn PDFs and photos with different layouts into structured values?"),
  B("**RQ3** - What are the main limitations of a rule-based reference table combined with an optional language model for explaining medical results?"),

  H2("2.2 Research Contributions"),
  B("An integrated Streamlit chatbot that accepts PDFs, photos and pasted text and explains blood test values."),
  B("A reference table of 55 markers with 248 alias names, male and female ranges, urgent thresholds and plain-language explanations of what a high or low value can mean."),
  B("A position-based row reconstruction step so that table cells from PDFs and OCR output stay on one line."),
  B("An evaluation step that prefers the range printed on the report, applies sex-specific ranges otherwise, grades severity and flags urgent values."),
  B("Safeguards: ratio and unmatched lines are reported rather than guessed, a disclaimer accompanies answers, and urgent values prompt the user to contact a doctor."),

  H2("2.3 Methodology"),
  P("The workflow is data-grounded. The user chooses a sex (optional) and uploads a file or pastes text. If the file is a PDF with a text layer, words are read with their coordinates; if it is a photo or a scanned PDF, the pages are passed through RapidOCR. In both cases the words are grouped into rows by vertical position and sorted left to right, which rebuilds table rows such as `Hemoglobin  10.2  g/dL  12.0 - 15.0`."),
  P("Each row is matched against the alias list, longest alias first so that `HbA1c` is not mistaken for `Hemoglobin`. The first number after the name is taken as the value, the following text as the unit, and a pair of numbers joined by a dash as the printed reference range. Platelet and white-cell counts are converted to cells/uL when printed in lakhs or thousands. The evaluator compares the value with the report's range, or with the stored range if none is printed, and checks the urgent thresholds. Explanations are then read from the reference table. For chat, questions that name a marker are answered from the table; questions about \"abnormal\" results or a \"summary\" are answered from the evaluated findings; other questions go to the language model if a key is configured, with the evaluated results as the only context."),

  img("architecture.png", 560, 373),
  CAP("Figure 1: Work-flow chart of LabLens"),

  H2("2.4 Description of Corpora"),
  P("LabLens does not train a model, so its data are a lookup corpus and test inputs rather than a training set. The main corpus is the marker reference table `data/markers.csv`, compiled by the project team. It has 55 rows (one per marker) and 15 columns, in five groups: identity fields (Key, Name, Category, Aliases, Unit); reference ranges (Male_Low, Male_High, Female_Low, Female_High); urgent thresholds (Critical_Low, Critical_High); plain-language text (What_It_Is, If_High, If_Low); and the source of each range (Range_Source)."),
  P("The file holds 248 distinct alias names (the aliases listed in the file plus each marker's own name), so that `Hb`, `HGB` and `Haemoglobin` all map to hemoglobin. Seven markers have separate male and female ranges (hemoglobin, hematocrit, ESR, HDL, creatinine, GGT and ferritin). Nine markers have an urgent low threshold and ten have an urgent high threshold. A check of the file found no duplicate keys, no alias that belongs to two markers, no empty unit or explanation fields, and no range whose low value is not below its high value; a test also checks that every marker records a range source."),
  table([3900, 2200, 3538], [
    ["Corpus", "Size", "Purpose"],
    ["Marker reference table (`data/markers.csv`)", "55 rows x 15 columns", "Aliases, reference ranges, urgent thresholds and plain-language explanations used by the parser, evaluator and chat."],
    ["Sample lab report (`samples/sample_report.txt`, also as `sample_report.pdf`)", "19 test rows (22 lines)", "End-to-end test input written by the team; contains no real patient data."],
    ["Generated test reports (in `tests/test_pipeline.py`)", "One 3-row table, as a PDF and as an image", "Checks of PDF row reconstruction and photo OCR."],
  ]),
  gap(),
  P("The 55 markers are spread over eleven categories, as shown below.", { keepNext: true }),
  table([4800, 1500, 3338], [
    ["Category", "Markers", "Examples"],
    ["Blood count", "15", "Hemoglobin, RBC, MCV, WBC, Platelets, ESR"],
    ["Liver", "9", "SGOT, SGPT, ALP, bilirubin, albumin"],
    ["Lipids", "5", "Total cholesterol, LDL, HDL, triglycerides, VLDL"],
    ["Blood sugar", "4", "Fasting, post-meal and random glucose, HbA1c"],
    ["Kidney", "4", "Creatinine, urea, BUN, uric acid"],
    ["Thyroid", "4", "TSH, total T3, total T4, free T4"],
    ["Iron", "4", "Ferritin, serum iron, TIBC, transferrin saturation"],
    ["Electrolytes", "3", "Sodium, potassium, chloride"],
    ["Minerals", "3", "Calcium, phosphorus, magnesium"],
    ["Vitamins", "3", "Vitamin D, vitamin B12, folate"],
    ["Inflammation", "1", "CRP"],
  ]),
  gap(),
  img("fig_raw_sample_report.png", 470, 340),
  CAP("Figure 2: Raw, unannotated input. The sample lab report as the chatbot receives it (rendered from samples/sample_report.txt). Of its 19 test rows, 18 are recognised; the cholesterol / HDL ratio row is deliberately not interpreted."),
  img("fig_reference_table.png", 620, 156),
  CAP("Figure 3: Annotated reference table. The first nine rows of data/markers.csv, showing identity, range and urgent-threshold columns (the explanation columns are not shown)."),
  H3("2.4.1 Source check of the reference ranges"),
  P("The reference ranges were checked marker by marker against published sources, and the table was corrected where it differed. The main source is the ABIM Laboratory Test Reference Ranges, revised January 2026 [8], which lists 50 of the 55 markers directly. The haemoglobin lower limits (13 g/dL for men, 12 g/dL for women) follow the WHO anaemia cut-offs [10]. The diabetes and prediabetes cut-offs quoted in the explanations (fasting glucose 100 to 125 and 126 or more, 2-hour glucose 140 to 199 and 200 or more, HbA1c 5.7 to 6.4 and 6.5 or more) match Tables 2.1 and 2.2 of the ADA Standards of Care in Diabetes 2026 [9]. The vitamin D wording refers to the 2011 Endocrine Society guideline [11]."),
  P("The check found that 41 of the 55 markers had at least one range limit that differed from ABIM, usually by a small amount: for example potassium up to 5.1 instead of 5.0, alkaline phosphatase 44 to 147 instead of 30 to 120, sodium from 135 instead of 136, and folate 3 to 17 instead of 1.8 to 9.0. These were corrected. Fourteen markers already matched. The corrected table records the source of every range in a `Range_Source` column."),
  table([3300, 1200, 5138], [
    ["Basis of the range", "Markers", "Notes"],
    ["Listed directly in ABIM, January 2026", "50", "Ranges taken as printed; haemoglobin lower limits use the WHO 2011 cut-offs."],
    ["Derived from ABIM values", "3", "Neutrophils (segmented 50-70 plus bands up to 5), urea (BUN 8-20 x 2.14) and VLDL (triglycerides / 5)."],
    ["ADA Standards of Care 2026", "1", "Post-meal glucose, using the 2-hour glucose cut-off of 140 mg/dL as an approximation."],
    ["Chosen by the team", "1", "Random glucose (70-140); no reference-interval source was found."],
  ]),
  gap(),
  P("What was not source-verified: the urgent thresholds for ten markers (haemoglobin, white cells, platelets, the three glucose tests, creatinine, sodium, potassium and calcium) are the team's conservative choices, because neither ABIM nor ADA publishes them in the documents consulted. The HDL upper limit of 100 mg/dL is also the team's choice. The plain-language explanations were written by the team, and only the numeric cut-offs named above were checked against the sources. The WHO anaemia cut-offs could not be read from the WHO document itself during this check; they were confirmed only from secondary reproductions of it, so please verify them in the WHO publication. ABIM is a US reference, and laboratories in India can print different ranges, which is why the application prefers the range printed on the report."),
  P("Dataset limitations: the urgent thresholds and the plain-language explanations were written by the team and have not been clinically reviewed. Ranges differ between laboratories and methods, and for children, pregnancy and older adults. The table covers 55 common markers and is not a complete test catalogue."),

  H2("2.5 Implementation"),
  H3("2.5.1 Chat interface"),
  P("`app.py` configures the Streamlit page and provides a sidebar with a sex selector, a file uploader (PDF, PNG, JPG, WEBP), a paste box and buttons to explain or reset. The main area shows summary counts, a three-tab view (results table, explanations, the raw text that was read) and the chat. Showing the raw text lets the user check what the reader extracted against the original report."),
  H3("2.5.2 Data loading"),
  P("`data_loader.py` checks that the reference file exists, reads it with Pandas, fills missing cells with empty strings and converts the range and urgent-threshold columns to numbers. It also builds the alias index, sorted so that longer aliases are tried first."),
  H3("2.5.3 Text extraction"),
  P("`extractor.py` reads a PDF's words with coordinates and groups them into rows using the median word height as a tolerance. If the PDF has fewer than 40 characters of text it is treated as scanned: pages are rendered at 200 dpi and passed to RapidOCR. Image uploads go straight to OCR. Pasted text is used as it is."),
  H3("2.5.4 Parsing"),
  P("`report_parser.py` removes serial numbers and bullets, matches the start of each line to an alias, and skips bracketed tags such as `(AST)`. It reads the value (including `<` and `>` qualifiers), the unit and the printed range. It ignores H / L flag columns without damaging units such as `mmol/L`, converts platelets and white-cell counts from lakhs or thousands, keeps only the first reading of each marker, and records lines that look like results but match no marker. Lines such as `Cholesterol/HDL Ratio` are not read as total cholesterol."),
  H3("2.5.5 Evaluation"),
  P("`evaluator.py` chooses the range: the report's own range if one was parsed, otherwise the stored male, female or combined range depending on the selected sex. A value beyond an urgent threshold is labelled URGENT. Other out-of-range values are labelled low or high, with a severity of slightly (up to 10 percent beyond the limit), moderately (up to 30 percent) or markedly (more than 30 percent). Notes record when a unit was converted, when the report's own range was used, or when a combined range was applied because no sex was given."),
  H3("2.5.6 Explanation and chat"),
  P("`explainer.py` builds the results table, the per-test explanation, an overall summary and the chat answers. Questions that name one or more markers (using the same alias list) are answered from the reference table, including markers that are not in the uploaded report. Questions about out-of-range values or a summary are answered from the evaluated findings. A disclaimer is added to the answers."),
  H3("2.5.7 Optional language model"),
  P("`llm.py` loads the key from the `.env` file and, only if a key is present, sends the question, the evaluated results and up to eight recent messages to the Groq API. The system prompt instructs the model to use only the supplied results, not to diagnose or name medicines, to say when something is not in the report, to recommend seeing a doctor and to flag urgent values. Errors from the service are caught so the chat does not crash."),
  H3("2.5.8 Configuration and dependencies"),
  P("`requirements.txt` lists Streamlit, Pandas, Groq, python-dotenv, PyMuPDF, Pillow, RapidOCR and pytest. The `.env` file holds the optional API key and must not be shared. The README gives run instructions."),
  H3("2.5.9 Testing approach"),
  P("`tests/test_pipeline.py` defines 17 automated checks covering: loading of the reference table; pasted values with abbreviations; separating HbA1c from hemoglobin; male and female ranges; precedence of the report's printed range; urgent potassium; platelet lakh conversion; ignoring a ratio row; units ending in L and H / L flag columns; bracketed aliases; the end-to-end sample report; chat answers for a marker in and not in the report; reassembly of table rows from a generated PDF; OCR of a generated photo of a report; that every marker records a range source and a valid range; and spot checks of three ranges against the cited sources."),

  H2("2.6 Results"),
  P("The results below describe observed behaviour of the code. They are functional observations from the project's own test cases and one demonstration run. They are not a benchmark of accuracy on real laboratory reports and not a claim of clinical validation."),
  H3("2.6.1 Automated tests"),
  P("All 17 tests passed in the final run (about 10 seconds on the development machine, including OCR). During development three tests initially failed. One exposed a real defect: a printed platelet range in lakhs (1.5 - 4.1) was multiplied by the wrong factor, so a normal count was flagged high. The other two were wrong expectations in the tests (a normal female haemoglobin of 13.5 g/dL was expected to be high, and the sample report has 18 recognisable rows, not 19). The platelet logic was fixed and the tests corrected. A later check of the running application showed the unit `mmol/L` being shortened to `mmol/` because an H / L flag cleanup removed the final letter; this was fixed and a regression test was added. After the ranges were checked against the sources (section 2.4.1) the table was corrected, the haemoglobin test values were updated to the new limits, and two tests were added."),
  H3("2.6.2 Demonstration run"),
  P("Nine values were pasted into the application with no sex selected. All nine were recognised; one was in range and eight were outside it. Results are shown in Table 1 and Figure 4."),
  table([2300, 1900, 2300, 3138], [
    ["Test", "Value", "Range used", "Status"],
    ["Hemoglobin", "10.2 g/dL", "12 - 15 (from report)", "Moderately low"],
    ["MCV", "74 fL", "83 - 101 (from report)", "Moderately low"],
    ["HbA1c", "5.9 %", "4 - 5.6", "Slightly high"],
    ["LDL cholesterol", "138 mg/dL", "0 - 99", "Markedly high"],
    ["TSH", "6.8 uIU/mL", "0.5 - 4", "Markedly high"],
    ["Vitamin D (25-OH)", "14 ng/mL", "30 - 60", "Markedly low"],
    ["Ferritin", "8 ng/mL", "24 - 336 (combined)", "Markedly low"],
    ["Potassium", "6.8 mmol/L", "3.5 - 5", "URGENT high"],
    ["Creatinine", "0.8 mg/dL", "0.5 - 1.3 (combined)", "Normal"],
  ]),
  CAP("Table 1: Demonstration run on nine pasted values (ranges as corrected in section 2.4.1)"),
  img("shot_results_cropped.png", 560, 400),
  CAP("Figure 4: Results table and automatic summary in LabLens"),
  P("The same sample report was also uploaded as a PDF (`samples/sample_report.pdf`). The application read the PDF text layer and recognised 18 of the 19 test rows: 5 were in range and 13 were outside it, with potassium marked urgent. The cholesterol / HDL ratio row was listed as a line that could not be matched, as intended. Figures 5 to 7 show this run."),
  img("shot_explanations.png", 560, 360),
  CAP("Figure 5: Explanations tab, showing two out-of-range tests (out-of-range results only)"),
  img("shot_chat.png", 500, 319),
  CAP("Figure 6: Chat answer to \"What does my low hemoglobin mean?\""),
  img("shot_upload.png", 560, 360),
  CAP("Figure 7: PDF upload and the text the reader extracted (\"What I read\" tab, extraction method pdf-text)"),
  H3("2.6.3 Functional summary"),
  table([2300, 3800, 3538], [
    ["Functional area", "Evidence in source code", "Result interpretation"],
    ["Text extraction", "`extract_text()`: PDF text layer, scanned PDF and image OCR; row grouping", "Table rows from a generated PDF and a generated photo were reassembled and parsed in tests."],
    ["Parsing", "`parse_report()`: alias matching, value, unit, range, scale conversion", "Handles abbreviations, bracketed aliases, qualifiers and lakh / thousand scales; unmatched lines are listed."],
    ["Evaluation", "`evaluate()`: report range, sex-specific range, severity, urgent thresholds", "Produces low, normal, high and urgent labels with a severity grade."],
    ["Explanation and chat", "`answer()`, `explain_finding()`, `overall_summary()`", "Answers marker, abnormal-value and summary questions from the table without a language model."],
    ["Optional language model", "`ask_llm()` with a grounded system prompt", "Implemented; not exercised in this evaluation because no API key was configured."],
  ]),
  gap(),

  H2("2.7 Discussion"),
  H3("2.7.1 Reading PDF and photo reports"),
  B("Findings: rebuilding rows from word coordinates let a generated PDF table and an OCR'd image of the same table parse correctly in tests."),
  B("Interpretation: grouping by position is what makes line-based parsing possible for tabular reports, which plain text extraction usually splits into one cell per line."),
  B("Limitations: only simple generated tables were tested. Real reports with multi-column layouts, stamps, handwriting or poor photos may be misread, and OCR can confuse characters such as 0 and O or 1 and l."),
  B("Overall finding: extraction works on the tested layouts, and the \"What I read\" view lets users check it, but it is not validated on real reports."),
  H3("2.7.2 Range comparison and urgent values"),
  B("Findings: values are compared with the report's own range when available, and otherwise with a stored range; urgent thresholds are always applied."),
  B("Interpretation: using the laboratory's printed range respects differences in methods, while the stored ranges and urgent thresholds give a fallback and a safety net."),
  B("Limitations: the stored ranges were checked against ABIM 2026 and ADA 2026 (section 2.4.1), but the urgent thresholds and a few ranges are team-chosen and ABIM is a US reference; the severity bands (10 and 30 percent) are a simple convention; a combined range is used when sex is not given; ranges for children, pregnancy and older adults are not handled."),
  B("Overall finding: the logic is transparent and testable, but the thresholds need review by a clinician before any real use."),
  H3("2.7.3 Plain-language explanations and chat"),
  B("Findings: every marker has a written description of what it measures and what a high or low value can mean; marker questions are answered directly from this table."),
  B("Interpretation: keeping explanations in a reviewed table means the same question gets the same, controlled answer and avoids invented facts."),
  B("Limitations: the explanations are general and cannot account for the user's symptoms, history or medicines. Open-ended questions depend on the optional language model, which was not tested here."),
  B("Overall finding: the rule-based path is reliable for the supported markers; broader conversation is unverified."),
  H3("2.7.4 Safety and privacy"),
  B("Findings: answers carry a disclaimer; urgent values advise contacting a doctor; unrecognised and ratio lines are shown rather than guessed."),
  B("Interpretation: the tool aims to inform, not to replace medical advice."),
  B("Limitations: uploaded reports contain personal health information. If the Groq option is enabled, evaluated results (without the original file) are sent to an external service; this should be disclosed to users."),
  B("Overall finding: basic safeguards are present, but a real deployment would need privacy, consent and clinical review."),
  H3("Cross-cutting limitations"),
  B("No measured accuracy, precision or recall on real reports, no user study and no clinical validation was performed."),
  B("The marker table covers 55 tests; others are listed as unmatched lines."),
  B("The reference ranges were checked against published sources, but the urgent thresholds and the plain-language explanations were written by the team and need clinical review."),
  B("OCR quality depends on image quality; the reader may misread digits."),
  B("The optional language-model path needs a valid API key and network access and was not evaluated."),
  B("The tool does not diagnose and should not be used for medical decisions."),

  H2("2.8 Conclusion"),
  P("LabLens combines text extraction, OCR, alias-based parsing, range evaluation and a reference table of plain-language explanations in a single chatbot for blood test reports. Its strongest feature is that every value, range and status comes from deterministic code, so explanations stay tied to the report, while an optional language model can handle open-ended questions. Seventeen automated tests passed, and a demonstration run recognised nine of nine pasted values and correctly marked a dangerously high potassium as urgent."),
  P("The main limitations are the urgent thresholds and explanations that were not clinically reviewed, the lack of testing on real reports and the untested language-model path. Future work could include clinical review of the reference table, an evaluation on a de-identified set of real reports with measured extraction accuracy, support for more markers and for children's and pregnancy ranges, trend tracking across several reports, and local-language explanations."),

  H2("2.9 References"),
  P("1. LabLens project source code: app.py, data_loader.py, extractor.py, report_parser.py, evaluator.py, explainer.py, llm.py, tests/test_pipeline.py, data/markers.csv, README.md, requirements.txt (project archive supplied with this report).", { align: AlignmentType.LEFT }),
  refP("2. Streamlit documentation. https://docs.streamlit.io/"),
  refP("3. Pandas documentation. https://pandas.pydata.org/docs/"),
  refP("4. PyMuPDF documentation. https://pymupdf.readthedocs.io/"),
  refP("5. RapidOCR project. https://github.com/RapidAI/RapidOCR"),
  refP("6. Groq API documentation. https://console.groq.com/docs/overview"),
  P("7. Supplied dataset: data/markers.csv (compiled by the project team).", { align: AlignmentType.LEFT }),
  refP("8. American Board of Internal Medicine (ABIM). Laboratory Test Reference Ranges, revised January 2026. https://www.abim.org/media/e2wdwdqu/laboratory-reference-ranges.pdf"),
  refP("9. American Diabetes Association Professional Practice Committee. 2. Diagnosis and Classification of Diabetes: Standards of Care in Diabetes-2026. Diabetes Care 2026;49(Suppl 1):S27-S49. https://pmc.ncbi.nlm.nih.gov/articles/PMC12690183/"),
  refP("10. World Health Organization. Haemoglobin concentrations for the diagnosis of anaemia and assessment of severity. WHO/NMH/NHD/MNM/11.1, 2011. https://www.who.int/publications/i/item/WHO-nMH-NHD-MNM-11.1"),
  refP("11. Holick MF, Binkley NC, Bischoff-Ferrari HA, et al. Evaluation, treatment, and prevention of vitamin D deficiency: an Endocrine Society clinical practice guideline. J Clin Endocrinol Metab 2011;96(7):1911-1930. https://doi.org/10.1210/jc.2011-0385"),
];

const doc = new Document({
  creator: "LabLens project team",
  title: "LabLens CCA3 Report",
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 30, bold: true, font: FONT }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 25, bold: true, font: FONT }, paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 } },
      { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 22, bold: true, font: FONT }, paragraph: { spacing: { before: 140, after: 80 }, outlineLevel: 2 } },
    ],
  },
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 270 } } } }] }] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new TextRun({ text: "LabLens  |  Page ", font: FONT, size: 20 }), new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 20 })] })] }) },
    children: [...cover, ...body],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  const out = path.join(__dirname, process.argv[2] || "LabLens_CCA3_Report.docx");
  fs.writeFileSync(out, buf);
  console.log("wrote", out);
});
