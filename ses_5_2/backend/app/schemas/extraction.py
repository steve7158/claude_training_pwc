from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class PatientDemographics(BaseModel):
    mrn: Optional[str] = None
    first_name: str
    last_name: str
    dob: Optional[date] = None
    gender: Optional[Literal["M", "F", "O"]] = None
    ssn: Optional[str] = None


class VitalSigns(BaseModel):
    temperature: Optional[float] = None
    temp_unit: Optional[Literal["F", "C"]] = None
    blood_pressure: Optional[str] = None  # "systolic/diastolic"
    heart_rate: Optional[int] = None
    respiratory_rate: Optional[int] = None
    oxygen_saturation: Optional[float] = None


class LabResult(BaseModel):
    test_name: str
    test_code: Optional[str] = None  # LOINC code
    result_value: float
    unit: str
    reference_range: Optional[str] = None
    normal_range_low: Optional[float] = None
    normal_range_high: Optional[float] = None
    result_date: Optional[datetime] = None
    status: Literal["normal", "abnormal", "critical", "unknown"] = "unknown"


class Medication(BaseModel):
    drug_name: str
    ndc_code: Optional[str] = None
    route: Optional[str] = None
    frequency: Optional[str] = None
    dosage: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    indication: Optional[str] = None


class ClinicalExtraction(BaseModel):
    demographics: PatientDemographics
    vitals: Optional[VitalSigns] = None
    chief_complaint: Optional[str] = None
    history_of_present_illness: Optional[str] = None
    medications: list[Medication] = Field(default_factory=list)
    allergies: list[str] = Field(default_factory=list)
    diagnoses: list[str] = Field(default_factory=list)
    procedures: list[str] = Field(default_factory=list)
    lab_results: list[LabResult] = Field(default_factory=list)
    assessment_and_plan: Optional[str] = None
    extraction_confidence: float = 0.0
    extraction_metadata: dict = Field(default_factory=dict)


class ValidationResultOut(BaseModel):
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    confidence_score: float


class ExtractionOut(BaseModel):
    document_id: str
    extraction_status: str
    extracted_data: Optional[ClinicalExtraction] = None
    validation_results: Optional[ValidationResultOut] = None
    confidence_score: float = 0.0
    processing_time_ms: int = 0
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None


class ExtractionUpdate(BaseModel):
    extracted_data: ClinicalExtraction
