"""Data Validation & Normalization (LLD §2.5) and Confidence Scoring
Algorithm (LLD §3)."""
import re

from sqlalchemy.orm import Session

from app.models.taxonomy import Icd10Code, LoincCode, NdcDrug
from app.schemas.extraction import ClinicalExtraction, ValidationResultOut

_MRN_FORMAT_RE = re.compile(r"^[A-Za-z0-9]{4,20}$")


def is_valid_mrn(mrn: str | None) -> bool:
    if mrn is None:
        return True  # optional field: absence is not a format error
    return bool(_MRN_FORMAT_RE.match(mrn))


def validate_and_normalize(
    db: Session, extraction: ClinicalExtraction
) -> tuple[ClinicalExtraction, ValidationResultOut]:
    errors: list[str] = []
    warnings: list[str] = []

    # --- Demographics ---
    if not is_valid_mrn(extraction.demographics.mrn):
        errors.append("Invalid MRN format")
    if not extraction.demographics.first_name or not extraction.demographics.last_name:
        errors.append("Missing patient name")

    # --- Lab results: LOINC lookup/normalization + range-based status ---
    for lab in extraction.lab_results:
        if lab.test_code:
            loinc = db.get(LoincCode, lab.test_code)
            if loinc is None:
                warnings.append(f"Unknown LOINC code: {lab.test_code}")
            else:
                lab.test_code = loinc.loinc_code
                if lab.normal_range_low is None:
                    lab.normal_range_low = loinc.normal_range_low
                if lab.normal_range_high is None:
                    lab.normal_range_high = loinc.normal_range_high

        if lab.normal_range_low is not None and lab.result_value < lab.normal_range_low:
            lab.status = "abnormal"
        elif lab.normal_range_high is not None and lab.result_value > lab.normal_range_high:
            lab.status = "abnormal"
        elif lab.normal_range_low is not None or lab.normal_range_high is not None:
            lab.status = "normal"

    # --- Medications: NDC lookup/normalization ---
    for med in extraction.medications:
        if med.ndc_code:
            ndc = db.get(NdcDrug, med.ndc_code)
            if ndc is None:
                warnings.append(f"Unknown NDC code: {med.ndc_code}")
            else:
                med.ndc_code = ndc.ndc_code
                med.drug_name = ndc.generic_name

    # --- Diagnoses: ICD-10 existence check (informational only) ---
    for dx in extraction.diagnoses:
        code_match = re.match(r"^([A-Za-z][0-9]{2}(?:\.[0-9A-Za-z]{1,4})?)", dx.strip())
        if code_match:
            code = code_match.group(1).upper()
            if db.get(Icd10Code, code) is None:
                warnings.append(f"Unknown ICD-10 code: {code}")

    is_valid = len(errors) == 0
    confidence_score = calculate_confidence(extraction, errors, warnings)

    validation = ValidationResultOut(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        confidence_score=confidence_score,
    )
    extraction.extraction_confidence = confidence_score
    return extraction, validation


def _demographics_confidence(extraction: ClinicalExtraction, errors: list[str]) -> float:
    return 0.98 if not errors else 0.6


def _vitals_confidence(extraction: ClinicalExtraction) -> float:
    return 0.9 if extraction.vitals is not None else 0.75


def _lab_results_confidence(extraction: ClinicalExtraction) -> float:
    if not extraction.lab_results:
        return 0.85
    known = sum(1 for lab in extraction.lab_results if lab.status != "unknown")
    return 0.7 + 0.3 * (known / len(extraction.lab_results))


def _medications_confidence(extraction: ClinicalExtraction) -> float:
    if not extraction.medications:
        return 0.85
    with_ndc = sum(1 for med in extraction.medications if med.ndc_code)
    return 0.75 + 0.25 * (with_ndc / len(extraction.medications))


def calculate_confidence(
    extraction: ClinicalExtraction, errors: list[str], warnings: list[str]
) -> float:
    """Mirrors LLD §3 `calculate_confidence` weighting exactly."""
    demographics_score = _demographics_confidence(extraction, errors)
    vitals_score = _vitals_confidence(extraction)
    lab_score = _lab_results_confidence(extraction)
    med_score = _medications_confidence(extraction)

    unknown_count = len([w for w in warnings if "unknown" in w.lower()])
    unknown_penalty = unknown_count * 0.02

    overall = (
        (demographics_score * 0.25)
        + (vitals_score * 0.15)
        + (lab_score * 0.35)
        + (med_score * 0.25)
        - unknown_penalty
    )
    return max(0.0, min(1.0, round(overall, 4)))
