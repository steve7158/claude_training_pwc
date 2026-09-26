import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.security import get_current_user, require_role
from app.db.session import get_db
from app.models.document import Document, DocumentType, ProcessingStatus
from app.models.extraction import Extraction
from app.models.audit import AuditLog
from app.models.user import Role, User
from app.schemas.document import AuditLogOut, DocumentListResponse, DocumentOut, DocumentUploadResponse
from app.schemas.extraction import ClinicalExtraction, ExtractionOut, ExtractionUpdate, ValidationResultOut
from app.services import export as export_service
from app.services.audit import write_audit_event
from app.services.pii import decrypt_extraction_dict, encrypt_extraction_dict
from app.services.storage import storage
from app.services.validation import validate_and_normalize
from app.worker.tasks import process_document_task

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=202)
def upload_document(
    file: UploadFile = File(...),
    document_type: DocumentType = Form(...),
    patient_id: uuid.UUID | None = Form(None),
    source_system: str = Form(...),
    db: Session = Depends(get_db),
    user: User = Depends(require_role(Role.admin, Role.clinician)),
):
    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    storage_path = storage.save(data, subdir="documents", filename=file.filename or "document")

    document = Document(
        patient_id=patient_id,
        document_type=document_type,
        source_system=source_system,
        original_filename=file.filename or "document",
        storage_path=storage_path,
        file_size=len(data),
        mime_type=file.content_type or "application/octet-stream",
        created_by=user.email,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    write_audit_event(db, document.id, "document_uploaded", user.email, {"filename": document.original_filename})

    process_document_task.delay(str(document.id))

    return DocumentUploadResponse(
        document_id=document.id,
        status="received",
        processing_status=document.processing_status,
        estimated_completion=(datetime.now(timezone.utc) + timedelta(seconds=5)).isoformat(),
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    status_filter: ProcessingStatus | None = Query(None, alias="status"),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Document)
    if status_filter is not None:
        q = q.filter(Document.processing_status == status_filter)
    total = q.count()
    items = q.order_by(Document.uploaded_at.desc()).offset(offset).limit(limit).all()
    return DocumentListResponse(total=total, items=items)


def _get_document_or_404(db: Session, document_id: uuid.UUID) -> Document:
    document = db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.get("/{document_id}", response_model=DocumentOut)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return _get_document_or_404(db, document_id)


def _build_extraction_out(document: Document, extraction: Extraction | None) -> ExtractionOut:
    if extraction is None:
        return ExtractionOut(
            document_id=str(document.id),
            extraction_status=document.processing_status.value,
        )
    decrypted = decrypt_extraction_dict(extraction.data)
    clinical = ClinicalExtraction.model_validate(decrypted)
    validation = extraction.validation
    return ExtractionOut(
        document_id=str(document.id),
        extraction_status=document.processing_status.value,
        extracted_data=clinical,
        validation_results=(
            ValidationResultOut(
                is_valid=validation.is_valid,
                errors=validation.errors,
                warnings=validation.warnings,
                confidence_score=validation.confidence_score,
            )
            if validation
            else None
        ),
        confidence_score=extraction.confidence_score,
        processing_time_ms=extraction.processing_time_ms,
        reviewed_by=extraction.reviewed_by,
        reviewed_at=extraction.reviewed_at,
    )


@router.get("/{document_id}/extraction", response_model=ExtractionOut)
def get_extraction(document_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    document = _get_document_or_404(db, document_id)
    extraction = db.query(Extraction).filter(Extraction.document_id == document_id).first()
    return _build_extraction_out(document, extraction)


@router.patch("/{document_id}/extraction", response_model=ExtractionOut)
def update_extraction(
    document_id: uuid.UUID,
    payload: ExtractionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(Role.admin, Role.clinician)),
):
    document = _get_document_or_404(db, document_id)
    extraction = db.query(Extraction).filter(Extraction.document_id == document_id).first()
    if extraction is None:
        raise HTTPException(status_code=404, detail="No extraction found for this document")

    extraction.data = encrypt_extraction_dict(payload.extracted_data.model_dump(mode="json"))
    extraction.reviewed_by = user.email
    extraction.reviewed_at = datetime.now(timezone.utc)
    db.add(extraction)
    db.commit()
    db.refresh(extraction)

    write_audit_event(db, document.id, "extraction_reviewed", user.email, {})
    return _build_extraction_out(document, extraction)


@router.post("/{document_id}/validate", response_model=ValidationResultOut)
def revalidate_extraction(
    document_id: uuid.UUID,
    payload: ExtractionUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_role(Role.admin, Role.clinician)),
):
    _get_document_or_404(db, document_id)
    _, validation = validate_and_normalize(db, payload.extracted_data)
    return validation


@router.get("/{document_id}/export")
def export_document(
    document_id: uuid.UUID,
    format: str = Query("fhir", pattern="^(fhir|hl7|csv)$"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    document = _get_document_or_404(db, document_id)
    extraction = db.query(Extraction).filter(Extraction.document_id == document_id).first()
    if extraction is None:
        raise HTTPException(status_code=404, detail="No completed extraction available for export")

    clinical = ClinicalExtraction.model_validate(decrypt_extraction_dict(extraction.data))
    write_audit_event(db, document.id, "document_exported", user.email, {"format": format})

    if format == "fhir":
        return export_service.to_fhir_bundle(str(document_id), clinical)
    if format == "hl7":
        return Response(content=export_service.to_hl7v2(str(document_id), clinical), media_type="text/plain")
    return Response(
        content=export_service.to_csv(clinical),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=extraction_{document_id}.csv"},
    )


@router.get("/{document_id}/audit", response_model=list[AuditLogOut])
def get_audit_trail(document_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    _get_document_or_404(db, document_id)
    return (
        db.query(AuditLog)
        .filter(AuditLog.document_id == document_id)
        .order_by(AuditLog.created_at.asc())
        .all()
    )
