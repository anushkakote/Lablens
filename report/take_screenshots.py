"""Captures the report screenshots from the running app (http://localhost:8501) using Edge."""
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(r"C:\Users\user\Desktop\Lab Report Explainer")
OUT = ROOT / "report"
PDF = ROOT / "samples" / "sample_report.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 900})
    page.goto("http://localhost:8501")
    page.wait_for_selector("input[type=file]", state="attached", timeout=60000)
    page.set_input_files("input[type=file]", str(PDF))
    page.get_by_role("button", name="Explain my report").click()
    page.wait_for_selector("text=I found", timeout=90000)
    page.wait_for_timeout(1500)

    # Figure 7: upload + extracted text
    page.get_by_role("tab", name="What I read").click()
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / "shot_upload.png"))

    # Figure 5: explanations tab
    page.get_by_role("tab", name="Explanations").click()
    page.wait_for_timeout(800)
    page.screenshot(path=str(OUT / "shot_explanations.png"))

    # Figure 6: chat question
    page.get_by_role("tab", name="Results table").click()
    box = page.locator("[data-testid=stChatInputTextArea]")
    box.fill("What does my low hemoglobin mean?")
    box.press("Enter")
    page.locator("[data-testid=stChatMessage]").get_by_text("What this result can mean").first.wait_for(timeout=60000)
    page.wait_for_timeout(1500)
    page.set_viewport_size({"width": 1400, "height": 2200})
    page.wait_for_timeout(1500)
    head = page.get_by_role("heading", name="Ask about your results").bounding_box()
    last = page.locator("[data-testid=stChatMessage]").last.bounding_box()
    top = head["y"] - 15
    page.screenshot(path=str(OUT / "shot_chat.png"), clip={
        "x": 340, "y": top, "width": 1020, "height": last["y"] + last["height"] + 20 - top})
    # Figure 4: pasted values (no printed ranges except haemoglobin and MCV)
    page2 = browser.new_page(viewport={"width": 1400, "height": 1500})
    page2.goto("http://localhost:8501")
    area = page2.get_by_placeholder("Hemoglobin 10.2 g/dL")
    area.fill("Hemoglobin 10.2 g/dL 12.0 - 15.0\nMCV 74 fL 83 - 101\nHbA1c 5.9 %\nLDL Cholesterol 138 mg/dL\n"
              "TSH 6.8 uIU/mL\nVitamin D (25-OH) 14 ng/mL\nFerritin 8 ng/mL\nSerum Potassium 6.8 mmol/L\n"
              "Creatinine 0.8 mg/dL")
    area.press("Control+Enter")
    page2.wait_for_timeout(800)
    page2.get_by_role("button", name="Explain my report").click()
    page2.locator("[data-testid=stChatMessage]").first.wait_for(timeout=60000)
    page2.wait_for_timeout(2500)
    page2.screenshot(path=str(OUT / "shot_results_new.png"))
    browser.close()
print("done")
