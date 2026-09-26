import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.models.document import DocumentType, ProcessingStatus


class DocumentUploadResponse(BaseModel):
    document_id: uuid.UUID
    status: str
    processing_status: ProcessingStatus
    estimated_completion: str


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    patient_id: Optional[uuid.UUID] = None
    document_type: DocumentType
    source_system: str
    original_filename: str
    file_size: int
    mime_type: str
    uploaded_at: datetime
    processing_status: ProcessingStatus
    error_message: Optional[str] = None
    created_by: str


class DocumentListResponse(BaseModel):
    total: int
    items: list[DocumentOut]


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    action: str
    actor: str
    detail: dict
    created_at: datetime
