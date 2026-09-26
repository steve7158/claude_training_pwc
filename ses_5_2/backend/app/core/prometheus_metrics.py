"""Custom Prometheus metrics named per LLD §6."""
from prometheus_client import Counter, Histogram

documents_processed_total = Counter(
    "documents_processed_total", "Documents processed", ["status"]
)
documents_processing_duration_ms = Histogram(
    "documents_processing_duration_ms", "Document processing duration in ms"
)
extraction_confidence_score = Histogram(
    "extraction_confidence_score", "Confidence score of completed extractions"
)
validation_errors_total = Counter(
    "validation_errors_total", "Total validation errors encountered"
)
