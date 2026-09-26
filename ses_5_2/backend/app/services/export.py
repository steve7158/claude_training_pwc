"""Structured Data Output (LLD §2.7): FHIR Bundle, HL7v2, and CSV export."""
import csv
import io
import uuid

from app.schemas.extraction import ClinicalExtraction


def to_fhir_bundle(document_id: str, extraction: ClinicalExtraction) -> dict:
    entries = []
    patient_id = str(uuid.uuid4())

    entries.append(
        {
            "resource": {
                "resourceType": "Patient",
                "id": patient_id,
                "identifier": (
                    [{"system": "urn:carta:mrn", "value": extraction.demographics.mrn}]
                    if extraction.demographics.mrn
                    else []
                ),
                "name": [
                    {
                        "given": [extraction.demographics.first_name],
                        "family": extraction.demographics.last_name,
                    }
                ],
                "gender": extraction.demographics.gender,
                "birthDate": extraction.demographics.dob.isoformat()
                if extraction.demographics.dob
                else None,
            }
        }
    )

    for lab in extraction.lab_results:
        entries.append(
            {
                "resource": {
                    "resourceType": "Observation",
                    "id": str(uuid.uuid4()),
                    "status": "final",
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "code": {
                        "coding": [
                            {
                                "system": "http://loinc.org",
                                "code": lab.test_code,
                                "display": lab.test_name,
                            }
                        ]
                    },
                    "valueQuantity": {"value": lab.result_value, "unit": lab.unit},
                    "interpretation": [{"text": lab.status}],
                }
            }
        )

    for med in extraction.medications:
        entries.append(
            {
                "resource": {
                    "resourceType": "MedicationStatement",
                    "id": str(uuid.uuid4()),
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "medicationCodeableConcept": {
                        "coding": (
                            [{"system": "http://hl7.org/fhir/sid/ndc", "code": med.ndc_code}]
                            if med.ndc_code
                            else []
                        ),
                        "text": med.drug_name,
                    },
                    "dosage": [{"text": f"{med.dosage or ''} {med.route or ''} {med.frequency or ''}".strip()}],
                }
            }
        )

    for dx in extraction.diagnoses:
        entries.append(
            {
                "resource": {
                    "resourceType": "Condition",
                    "id": str(uuid.uuid4()),
                    "subject": {"reference": f"Patient/{patient_id}"},
                    "code": {"text": dx},
                }
            }
        )

    return {
        "resourceType": "Bundle",
        "id": document_id,
        "type": "transaction",
        "entry": entries,
    }


def to_hl7v2(document_id: str, extraction: ClinicalExtraction) -> str:
    """Minimal HL7v2 ORU^R01-style message covering PID/OBR/OBX segments."""
    demo = extraction.demographics
    segments = [
        f"MSH|^~\\&|CARTA|CARTAHEALTHCARE|||{document_id}||ORU^R01|{document_id}|P|2.5",
        f"PID|1||{demo.mrn or ''}||{demo.last_name}^{demo.first_name}||{demo.dob or ''}|{demo.gender or ''}",
    ]
    for i, lab in enumerate(extraction.lab_results, start=1):
        segments.append(f"OBR|{i}|||{lab.test_code or ''}^{lab.test_name}")
        segments.append(
            f"OBX|{i}|NM|{lab.test_code or ''}^{lab.test_name}||{lab.result_value}|{lab.unit}|"
            f"{lab.reference_range or ''}|{lab.status.upper()}"
        )
    for i, med in enumerate(extraction.medications, start=1):
        segments.append(
            f"RXE|{i}|{med.ndc_code or ''}^{med.drug_name}|{med.dosage or ''}||{med.route or ''}|"
            f"{med.frequency or ''}"
        )
    return "\r".join(segments)


def to_csv(extraction: ClinicalExtraction) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["section", "field", "value"])
    demo = extraction.demographics
    for field, value in demo.model_dump().items():
        writer.writerow(["demographics", field, value])
    if extraction.vitals:
        for field, value in extraction.vitals.model_dump().items():
            writer.writerow(["vitals", field, value])
    for lab in extraction.lab_results:
        writer.writerow(["lab_result", lab.test_name, f"{lab.result_value} {lab.unit} ({lab.status})"])
    for med in extraction.medications:
        writer.writerow(["medication", med.drug_name, f"{med.dosage or ''} {med.route or ''} {med.frequency or ''}"])
    for dx in extraction.diagnoses:
        writer.writerow(["diagnosis", "", dx])
    for allergy in extraction.allergies:
        writer.writerow(["allergy", "", allergy])
    return buf.getvalue()
