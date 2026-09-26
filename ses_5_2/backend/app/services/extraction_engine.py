"""AI Data Extraction Engine (LLD §2.4). Calls Groq (free-tier LLM API) when
GROQ_API is configured; otherwise falls back to a deterministic mock
extractor so the app runs end-to-end without a key. Both paths return a
`ClinicalExtraction`.
"""
import json
import logging
import re
from datetime import date

from app.core.config import settings
from app.models.document import DocumentType
from app.schemas.extraction import ClinicalExtraction

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a clinical data extraction expert.
Extract all clinical information from the document.
Return ONLY a single structured JSON object matching the provided schema.
Do not include any prose, markdown fences, or explanation - JSON only."""

DOCUMENT_TYPE_PROMPTS: dict[DocumentType, str] = {
    DocumentType.discharge_summary: (
        "This is a hospital discharge summary. Pay close attention to the "
        "discharge diagnoses, discharge medications, and follow-up plan."
    ),
    DocumentType.lab_report: (
        "This is a laboratory report. Focus on extracting every lab test "
        "with its result value, unit, reference range, and LOINC code if present."
    ),
    DocumentType.imaging: (
        "This is an imaging/radiology report. Focus on the clinical indication, "
        "findings, and impression; extract diagnoses implied by the findings."
    ),
    DocumentType.progress_note: (
        "This is a clinical progress note. Focus on chief complaint, "
        "history of present illness, vitals, assessment, and plan."
    ),
}

SCHEMA_HINT = """
Return JSON with exactly this shape:
{
  "demographics": {"mrn": str|null, "first_name": str, "last_name": str, "dob": "YYYY-MM-DD"|null, "gender": "M"|"F"|"O"|null, "ssn": str|null},
  "vitals": {"temperature": number|null, "temp_unit": "F"|"C"|null, "blood_pressure": str|null, "heart_rate": int|null, "respiratory_rate": int|null, "oxygen_saturation": number|null} | null,
  "chief_complaint": str|null,
  "history_of_present_illness": str|null,
  "medications": [{"drug_name": str, "ndc_code": str|null, "route": str|null, "frequency": str|null, "dosage": str|null, "start_date": "YYYY-MM-DD"|null, "end_date": "YYYY-MM-DD"|null, "indication": str|null}],
  "allergies": [str],
  "diagnoses": [str],
  "procedures": [str],
  "lab_results": [{"test_name": str, "test_code": str|null, "result_value": number, "unit": str, "reference_range": str|null, "result_date": "YYYY-MM-DDTHH:MM:SS"|null}],
  "assessment_and_plan": str|null
}
"""


def get_extraction_prompt(document_type: DocumentType, normalized_text: str) -> str:
    type_hint = DOCUMENT_TYPE_PROMPTS.get(document_type, "")
    return f"{type_hint}\n{SCHEMA_HINT}\n\nDocument content:\n{normalized_text[:50000]}"


class ExtractionError(Exception):
    pass


def _strip_code_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    return text


def _call_groq(document_type: DocumentType, normalized_text: str) -> dict:
    from groq import Groq

    client = Groq(api_key=settings.groq_api_key)
    prompt = get_extraction_prompt(document_type, normalized_text)

    response = client.chat.completions.create(
        model=settings.groq_model,
        max_tokens=4096,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    raw_text = _strip_code_fences(response.choices[0].message.content or "")
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError as exc:
        logger.error("Groq returned non-JSON output: %s", raw_text[:500])
        raise ExtractionError(f"Failed to parse Groq response as JSON: {exc}") from exc


_MRN_RE = re.compile(r"\bMRN[:#]?\s*([A-Za-z0-9-]+)", re.IGNORECASE)
_NAME_RE = re.compile(r"\b(?:Patient|Name)[:\s]+([A-Za-z]+)[, ]+([A-Za-z]+)", re.IGNORECASE)
_DOB_RE = re.compile(r"\bDOB[:\s]+(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{4})")


def _mock_extract(document_type: DocumentType, normalized_text: str) -> dict:
    """Deterministic heuristic extractor used when no GROQ_API key is
    configured, so the full pipeline still runs end-to-end.
    """
    mrn_match = _MRN_RE.search(normalized_text)
    name_match = _NAME_RE.search(normalized_text)
    dob_match = _DOB_RE.search(normalized_text)

    first_name, last_name = "Unknown", "Patient"
    if name_match:
        last_name, first_name = name_match.group(1), name_match.group(2)

    dob = None
    if dob_match:
        raw = dob_match.group(1)
        try:
            if "/" in raw:
                m, d, y = raw.split("/")
                dob = date(int(y), int(m), int(d)).isoformat()
            else:
                dob = raw
        except ValueError:
            dob = None

    return {
        "demographics": {
            "mrn": mrn_match.group(1) if mrn_match else None,
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
            "gender": None,
            "ssn": None,
        },
        "vitals": None,
        "chief_complaint": None,
        "history_of_present_illness": None,
        "medications": [],
        "allergies": [],
        "diagnoses": [],
        "procedures": [],
        "lab_results": [],
        "assessment_and_plan": None,
    }


def extract_clinical_data(document_type: DocumentType, normalized_text: str) -> ClinicalExtraction:
    if settings.groq_api_key:
        raw = _call_groq(document_type, normalized_text)
        extraction_source = "groq"
    else:
        logger.warning("GROQ_API not set - using mock extractor")
        raw = _mock_extract(document_type, normalized_text)
        extraction_source = "mock"

    raw["extraction_confidence"] = 0.0  # filled in by validation/confidence step
    raw["extraction_metadata"] = {
        "model": settings.groq_model if extraction_source == "groq" else "mock-heuristic-v1",
        "source": extraction_source,
    }
    try:
        return ClinicalExtraction.model_validate(raw)
    except Exception as exc:
        raise ExtractionError(f"Extracted data failed schema validation: {exc}") from exc
