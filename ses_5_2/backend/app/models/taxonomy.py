from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class LoincCode(Base):
    __tablename__ = "loinc_codes"

    loinc_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    test_name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str | None] = mapped_column(String, nullable=True)
    component: Mapped[str | None] = mapped_column(String, nullable=True)
    property: Mapped[str | None] = mapped_column(String, nullable=True)
    system: Mapped[str | None] = mapped_column(String, nullable=True)
    scale_type: Mapped[str | None] = mapped_column(String, nullable=True)
    normal_range_low: Mapped[float | None] = mapped_column(Float, nullable=True)
    normal_range_high: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str | None] = mapped_column(String, nullable=True)


class NdcDrug(Base):
    __tablename__ = "ndc_drugs"

    ndc_code: Mapped[str] = mapped_column(String(11), primary_key=True)
    generic_name: Mapped[str] = mapped_column(String, nullable=False)
    brand_name: Mapped[str | None] = mapped_column(String, nullable=True)
    strength: Mapped[str | None] = mapped_column(String, nullable=True)
    unit_dose_form: Mapped[str | None] = mapped_column(String, nullable=True)
    route: Mapped[str | None] = mapped_column(String, nullable=True)
    manufacturer: Mapped[str | None] = mapped_column(String, nullable=True)


class Icd10Code(Base):
    __tablename__ = "icd10_codes"

    code: Mapped[str] = mapped_column(String(10), primary_key=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    short_description: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str | None] = mapped_column(String, nullable=True)


class SnomedCode(Base):
    __tablename__ = "snomed_codes"

    snomed_id: Mapped[str] = mapped_column(String, primary_key=True)
    preferred_term: Mapped[str] = mapped_column(String, nullable=False)
    hierarchy: Mapped[str | None] = mapped_column(Text, nullable=True)
