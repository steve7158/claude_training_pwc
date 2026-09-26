"""Processing Queue & Async Jobs (LLD §2.8), including the Error Handling &
Retry Logic from LLD §4 (exponential backoff, max 3 retries)."""
import time
import uuid
from datetime import datetime, timezone

from app.core.prometheus_metrics import (
    documents_processed_total,
    documents_processing_duration_ms,
    extraction_confidence_score,
    validation_errors_total,
)
from app.db.session import SessionLocal
from app.models.document import Document, ProcessingStatus
from app.models.extraction import Extraction, ValidationResult
from app.services.audit import write_audit_event
from app.services.extraction_engine import ExtractionError, extract_clinical_data
from app.services.pii import encrypt_extraction_dict
from app.services.preprocessing import UnsupportedDocumentError, preprocess_document
from app.services.validation import validate_and_normalize
from app.worker.celery_app import celery_app


class DocumentProcessingError(Exception):
    pass


class OCRError(DocumentProcessingError):
    pass


class ValidationPipelineError(DocumentProcessingError):
    pass


def _update_status(db, document: Document, status: ProcessingStatus, error_message: str | None = None):
    document.processing_status = status
    if status == ProcessingStatus.preprocessing and document.processing_started_at is None:
        document.processing_started_at = datetime.now(timezone.utc)
    if status in (ProcessingStatus.completed, ProcessingStatus.failed):
        document.processing_completed_at = datetime.now(timezone.utc)
    if error_message is not None:
        document.error_message = error_message
    db.add(document)
    db.commit()


@celery_app.task(bind=True, max_retries=3)
def process_document_task(self, document_id: str):
    db = SessionLocal()
    started_at = time.monotonic()
    document_uuid = uuid.UUID(document_id)
    try:
        document = db.get(Document, document_uuid)
        if document is None:
            return

        # Step 1: Preprocessing
        _update_status(db, document, ProcessingStatus.preprocessing)
        write_audit_event(db, document.id, "preprocessing_started", "system")
        try:
            normalized_text, sections, quality = preprocess_document(
                document.storage_path, document.mime_type
            )
        except UnsupportedDocumentError as exc:
            raise DocumentProcessingError(str(exc)) from exc

        # Step 2: Extraction
        _update_status(db, document, ProcessingStatus.processing)
        write_audit_event(db, document.id, "extraction_started", "system")
        extraction = extract_clinical_data(document.document_type, normalized_text)

        # Step 3: Validation & normalization
        extraction, validation_out = validate_and_normalize(db, extraction)

        # Step 4: Storage
        processing_time_ms = int((time.monotonic() - started_at) * 1000)
        extraction_dict = encrypt_extraction_dict(extraction.model_dump(mode="json"))

        extraction_row = Extraction(
            document_id=document.id,
            data=extraction_dict,
            confidence_score=validation_out.confidence_score,
            extraction_metadata={**extraction.extraction_metadata, "quality": quality, "sections": list(sections.keys())},
            processing_time_ms=processing_time_ms,
        )
        db.add(extraction_row)
        db.flush()

        db.add(
            ValidationResult(
                extraction_id=extraction_row.id,
                is_valid=validation_out.is_valid,
                errors=validation_out.errors,
                warnings=validation_out.warnings,
                confidence_score=validation_out.confidence_score,
            )
        )

        _update_status(db, document, ProcessingStatus.completed)
        write_audit_event(
            db,
            document.id,
            "processing_completed",
            "system",
            {"confidence_score": validation_out.confidence_score, "processing_time_ms": processing_time_ms},
        )
        documents_processed_total.labels(status="completed").inc()
        documents_processing_duration_ms.observe(processing_time_ms)
        extraction_confidence_score.observe(validation_out.confidence_score)
        validation_errors_total.inc(len(validation_out.errors))
    except Exception as exc:  # noqa: BLE001 - top-level task boundary
        db.rollback()
        document = db.get(Document, document_uuid)
        if document is not None:
            _update_status(db, document, ProcessingStatus.failed, error_message=str(exc))
            write_audit_event(db, document.id, "processing_failed", "system", {"error": str(exc)})
            documents_processed_total.labels(status="failed").inc()
        try:
            raise self.retry(exc=exc, countdown=2 ** self.request.retries)
        except Exception:
            pass
    finally:
        db.close()
