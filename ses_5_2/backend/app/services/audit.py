import uuid

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def write_audit_event(db: Session, document_id: uuid.UUID, action: str, actor: str, detail: dict | None = None) -> None:
    entry = AuditLog(document_id=document_id, action=action, actor=actor, detail=detail or {})
    db.add(entry)
    db.commit()
