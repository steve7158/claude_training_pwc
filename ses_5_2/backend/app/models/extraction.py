import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Extraction(Base):
    __tablename__ = "extractions"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("documents.id"), unique=True, nullable=False)
    # PII fields (mrn/ssn) inside `data` are encrypted at rest - see core/encryption.py
    data: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    extraction_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    processing_time_ms: Mapped[int] = mapped_column(Integer, default=0)
    reviewed_by: Mapped[str | None] = mapped_column(nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    validation: Mapped["ValidationResult"] = relationship(
        back_populates="extraction", uselist=False, cascade="all, delete-orphan"
    )


class ValidationResult(Base):
    __tablename__ = "validation_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    extraction_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extractions.id"), unique=True, nullable=False)
    is_valid: Mapped[bool] = mapped_column(default=True)
    errors: Mapped[list] = mapped_column(JSON, default=list)
    warnings: Mapped[list] = mapped_column(JSON, default=list)
    confidence_score: Mapped[float] = mapped_column(Float, default=1.0)

    extraction: Mapped[Extraction] = relationship(back_populates="validation")
