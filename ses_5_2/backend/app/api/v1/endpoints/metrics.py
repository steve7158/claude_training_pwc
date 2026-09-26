from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.document import Document, ProcessingStatus
from app.models.extraction import Extraction

router = APIRouter(prefix="/metrics", tags=["metrics"], dependencies=[Depends(get_current_user)])


def _percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = min(len(values) - 1, int(round(pct * (len(values) - 1))))
    return values[idx]


@router.get("/summary")
def metrics_summary(db: Session = Depends(get_db)):
    total_documents = db.query(func.count(Document.id)).scalar() or 0
    status_counts = dict(
        db.query(Document.processing_status, func.count(Document.id)).group_by(Document.processing_status).all()
    )
    status_counts = {status.value if hasattr(status, "value") else status: count for status, count in status_counts.items()}

    completed = status_counts.get(ProcessingStatus.completed.value, 0)
    failed = status_counts.get(ProcessingStatus.failed.value, 0)

    avg_confidence = db.query(func.avg(Extraction.confidence_score)).scalar() or 0.0
    processing_times = [row[0] for row in db.query(Extraction.processing_time_ms).all()]
    avg_processing_time_ms = sum(processing_times) / len(processing_times) if processing_times else 0.0
    p95_latency_ms = _percentile([float(t) for t in processing_times], 0.95)

    error_rate = (failed / total_documents * 100) if total_documents else 0.0
    accuracy_rate = avg_confidence * 100

    return {
        "total_documents": total_documents,
        "status_counts": status_counts,
        "documents_completed": completed,
        "documents_failed": failed,
        "accuracy_rate": round(accuracy_rate, 2),
        "avg_processing_time_ms": round(avg_processing_time_ms, 2),
        "p95_latency_ms": round(p95_latency_ms, 2),
        "error_rate": round(error_rate, 2),
    }
