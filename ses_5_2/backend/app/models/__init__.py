"""Importing this package registers every model on Base.metadata - required
before Base.metadata.create_all(). Import `app.models` (not individual
model modules) whenever you need all tables registered, to avoid the
circular import that comes from having db/base.py import models itself.
"""
from app.models.audit import AuditLog  # noqa: F401
from app.models.document import Document, DocumentPage  # noqa: F401
from app.models.extraction import Extraction, ValidationResult  # noqa: F401
from app.models.taxonomy import Icd10Code, LoincCode, NdcDrug, SnomedCode  # noqa: F401
from app.models.user import Role, User  # noqa: F401
