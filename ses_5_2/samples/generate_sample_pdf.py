"""Generates sample clinical document PDFs for testing the Carta Healthcare
upload flow. Text is drawn as real selectable text (not a scanned image),
so the app's pypdf-based preprocessing extracts it directly.

Usage: python generate_sample_pdf.py
"""
import os

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

OUT_DIR = os.path.dirname(os.path.abspath(__file__))


def draw_document(filename: str, title: str, lines: list[str]):
    path = os.path.join(OUT_DIR, filename)
    c = canvas.Canvas(path, pagesize=letter)
    width, height = letter
    x_margin = 0.75 * inch
    y = height - 0.75 * inch

    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_margin, y, title)
    y -= 0.35 * inch

    c.setFont("Helvetica", 10)
    for line in lines:
        if y < 0.75 * inch:
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 0.75 * inch
        if line.startswith("## "):
            c.setFont("Helvetica-Bold", 11)
            y -= 0.05 * inch
            c.drawString(x_margin, y, line[3:])
            c.setFont("Helvetica", 10)
            y -= 0.22 * inch
        elif line == "":
            y -= 0.15 * inch
        else:
            c.drawString(x_margin, y, line)
            y -= 0.18 * inch

    c.save()
    print(f"Wrote {path}")


DISCHARGE_SUMMARY = [
    "Facility: Carta Memorial Hospital",
    "Encounter Type: Inpatient Discharge Summary",
    "",
    "## Patient Demographics",
    "Patient: Nguyen, Linda",
    "MRN: MRN48213",
    "DOB: 11/02/1958",
    "Sex: F",
    "",
    "## Chief Complaint",
    "Worsening shortness of breath and lower extremity edema.",
    "",
    "## History of Present Illness",
    "72-year-old female with a history of congestive heart failure presented",
    "with a 5-day history of progressive dyspnea on exertion, orthopnea, and",
    "bilateral lower extremity swelling. No chest pain. No fever.",
    "",
    "## Vital Signs",
    "Temp: 98.4 F   BP: 142/88   HR: 96   RR: 20   SpO2: 93%",
    "",
    "## Laboratory Results",
    "Sodium 133 mmol/L",
    "Potassium 4.6 mmol/L",
    "Creatinine 1.6 mg/dL",
    "BUN 28 mg/dL",
    "Hemoglobin A1c 7.2 %",
    "",
    "## Allergies",
    "Sulfa drugs",
    "",
    "## Discharge Medications",
    "furosemide 40mg oral twice daily",
    "lisinopril 10mg oral once daily",
    "metoprolol succinate 50mg oral once daily",
    "",
    "## Discharge Diagnoses",
    "I50.9 Heart failure, unspecified",
    "N18.3 Chronic kidney disease, stage 3",
    "E11.9 Type 2 diabetes mellitus without complications",
    "",
    "## Procedures",
    "Transthoracic echocardiogram",
    "",
    "## Assessment and Plan",
    "Patient treated for acute decompensated heart failure with IV diuresis,",
    "transitioned to oral furosemide with good response. Renal function stable.",
    "Discharge home with home health nursing and cardiology follow-up in 1 week.",
    "Daily weights and low-sodium diet reinforced with patient and family.",
]

if __name__ == "__main__":
    draw_document(
        "sample_discharge_summary.pdf",
        "Carta Memorial Hospital - Discharge Summary",
        DISCHARGE_SUMMARY,
    )
