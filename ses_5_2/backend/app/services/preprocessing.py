"""Document Preprocessing Pipeline (LLD §2.2)."""
import io
import re

from pypdf import PdfReader

from app.services.storage import storage


class UnsupportedDocumentError(Exception):
    pass


def _extract_pdf_text(data: bytes) -> tuple[str, int]:
    reader = PdfReader(io.BytesIO(data))
    pages_text = []
    for page in reader.pages:
        pages_text.append(page.extract_text() or "")
    return "\n\n".join(pages_text), len(reader.pages)


def _parse_hl7(data: bytes) -> str:
    """Very small HL7v2 pipe-delimited parser: turns segments into
    readable "SEGMENT: field | field | ..." lines the LLM can reason about.
    """
    text = data.decode("utf-8", errors="ignore")
    lines = []
    for segment in text.replace("\r", "\n").split("\n"):
        segment = segment.strip()
        if not segment:
            continue
        fields = segment.split("|")
        lines.append(f"{fields[0]}: " + " | ".join(fields[1:]))
    return "\n".join(lines)


def normalize_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


SECTION_HEADERS = [
    "chief complaint",
    "history of present illness",
    "past medical history",
    "medications",
    "allergies",
    "vital signs",
    "physical exam",
    "laboratory results",
    "assessment and plan",
    "diagnoses",
]


def segment_document(text: str) -> dict[str, str]:
    """Best-effort split into named sections by scanning for known headers."""
    sections: dict[str, str] = {}
    lowered = text.lower()
    positions = []
    for header in SECTION_HEADERS:
        idx = lowered.find(header)
        if idx != -1:
            positions.append((idx, header))
    positions.sort()
    for i, (idx, header) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        sections[header] = text[idx:end].strip()
    if not sections:
        sections["full_text"] = text
    return sections


def assess_quality(text: str, page_count: int, is_scanned: bool) -> dict:
    has_structured_elements = bool(re.search(r"\b(mrn|dob|patient)\b", text.lower()))
    confidence = 0.95 if text and len(text.strip()) > 50 else 0.4
    warnings = []
    if not text or len(text.strip()) < 50:
        warnings.append("Extracted text is very short; document may be low quality or unsupported.")
    return {
        "quality_score": confidence,
        "is_scanned": is_scanned,
        "has_structured_elements": has_structured_elements,
        "page_count": page_count,
        "confidence_score": confidence,
        "warnings": warnings,
    }


def preprocess_document(storage_path: str, mime_type: str) -> tuple[str, dict[str, str], dict]:
    """Mirrors LLD §2.2 `preprocess_document`. Returns (normalized_text,
    sections, quality_assessment).

    OCR is intentionally not implemented in this build (scoped out per
    plan) - image/scanned documents are flagged via `is_scanned` and
    quality warnings rather than silently producing empty text.
    """
    data = storage.read(storage_path)
    is_scanned = False
    page_count = 1

    if mime_type == "application/pdf":
        text, page_count = _extract_pdf_text(data)
        if not text.strip():
            is_scanned = True
            text = ""
    elif mime_type.startswith("image/"):
        is_scanned = True
        text = ""
    elif mime_type in ("application/hl7", "application/hl7-v2", "text/hl7"):
        text = _parse_hl7(data)
    elif mime_type.startswith("text/"):
        text = data.decode("utf-8", errors="ignore")
    else:
        raise UnsupportedDocumentError(f"Unsupported mime type: {mime_type}")

    normalized = normalize_text(text)
    sections = segment_document(normalized)
    quality = assess_quality(normalized, page_count, is_scanned)
    if is_scanned:
        quality["warnings"].append(
            "Document appears to be a scanned image; OCR is not enabled in this deployment."
        )
    return normalized, sections, quality
