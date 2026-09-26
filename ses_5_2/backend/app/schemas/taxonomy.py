from pydantic import BaseModel, ConfigDict


class LoincCodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    loinc_code: str
    test_name: str
    short_name: str | None = None
    normal_range_low: float | None = None
    normal_range_high: float | None = None
    unit: str | None = None


class NdcDrugOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ndc_code: str
    generic_name: str
    brand_name: str | None = None
    route: str | None = None


class Icd10CodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    code: str
    description: str
    category: str | None = None


class SnomedCodeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    snomed_id: str
    preferred_term: str
