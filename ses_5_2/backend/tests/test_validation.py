from app.models.taxonomy import LoincCode
from app.schemas.extraction import ClinicalExtraction, LabResult, PatientDemographics
from app.services.validation import calculate_confidence, is_valid_mrn, validate_and_normalize


def test_is_valid_mrn():
    assert is_valid_mrn(None) is True
    assert is_valid_mrn("ABC12345") is True
    assert is_valid_mrn("a") is False
    assert is_valid_mrn("bad mrn!") is False


def test_loinc_normalization_and_range_status(db_session):
    db_session.add(
        LoincCode(
            loinc_code="2345-7",
            test_name="Glucose",
            normal_range_low=70,
            normal_range_high=100,
            unit="mg/dL",
        )
    )
    db_session.commit()

    extraction = ClinicalExtraction(
        demographics=PatientDemographics(mrn="MRN12345", first_name="Jane", last_name="Doe"),
        lab_results=[LabResult(test_name="Glucose", test_code="2345-7", result_value=180, unit="mg/dL")],
    )

    result, validation = validate_and_normalize(db_session, extraction)

    assert result.lab_results[0].status == "abnormal"
    assert result.lab_results[0].normal_range_high == 100
    assert validation.is_valid is True
    assert not any("Unknown LOINC" in w for w in validation.warnings)


def test_unknown_loinc_code_produces_warning_and_penalty(db_session):
    extraction = ClinicalExtraction(
        demographics=PatientDemographics(mrn="MRN12345", first_name="Jane", last_name="Doe"),
        lab_results=[LabResult(test_name="Mystery Test", test_code="99999-9", result_value=1, unit="U")],
    )
    _, validation = validate_and_normalize(db_session, extraction)
    assert any("Unknown LOINC code: 99999-9" in w for w in validation.warnings)


def test_calculate_confidence_bounds():
    extraction = ClinicalExtraction(
        demographics=PatientDemographics(mrn="MRN1", first_name="A", last_name="B"),
    )
    score = calculate_confidence(extraction, errors=[], warnings=[])
    assert 0.0 <= score <= 1.0

    score_with_errors = calculate_confidence(extraction, errors=["Invalid MRN format"], warnings=["unknown code"])
    assert score_with_errors < score
