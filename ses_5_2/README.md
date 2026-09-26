# Carta Healthcare — Clinical Data Extraction Platform

A full-stack implementation of the system described in `hld.md` / `lld.md`:
upload a clinical document, extract structured data with an LLM, validate it
against clinical taxonomies, score confidence, review/correct it, and export
FHIR/HL7/CSV — with JWT auth, RBAC, an audit trail, and Prometheus metrics.

## Stack

- **Backend**: FastAPI (Python 3.11), SQLAlchemy 2.0, Celery + Redis for async
  processing, PostgreSQL, Groq API (`groq` SDK, free-tier LLM, model
  `openai/gpt-oss-120b`) for extraction. The LLD specifies Claude; this
  build swaps in Groq's free tier so it runs with no paid API key (see
  `app/services/extraction_engine.py` — swapping back to Claude/another
  provider is a new `_call_*` function, not a rewrite).
- **Frontend**: React + TypeScript + Vite + Tailwind.
- **Infra**: Docker Compose (postgres, redis, backend, worker, frontend).

## Quick start

```bash
cp .env.example .env       # already done in this checkout; edit if you want your own Groq key
docker compose up --build
```

- Frontend: http://localhost:5174
- Backend API docs: http://localhost:8001/docs
- Prometheus metrics: http://localhost:8001/metrics

Demo accounts (seeded automatically on first backend startup):

| Role      | Email                    | Password           |
|-----------|---------------------------|---------------------|
| admin     | admin@carta.health        | AdminPass123!       |
| clinician | clinician@carta.health    | ClinicianPass123!   |
| analyst   | analyst@carta.health      | AnalystPass123!     |

Admin/clinician can upload documents and review/edit extractions; analyst is
read-only + export.

## Groq API key

Leave `GROQ_API` blank in `.env` to run entirely on a built-in deterministic
mock extractor (regex/heuristic field pulls) — the full pipeline (preprocess
→ extract → validate → score → export → audit) still runs end-to-end with no
external calls. Set a real key (get one free at https://console.groq.com) to
switch to actual LLM extraction (`app/services/extraction_engine.py`); no
other code changes needed. `GROQ_MODEL` defaults to `openai/gpt-oss-120b`
and can be overridden to any Groq-hosted model.

## Backend tests

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

Tests run against SQLite and Celery's eager mode (no Postgres/Redis needed).

## What's scoped down from the LLD, and why

The LLD's infra targets a large enterprise deployment. For a runnable local
app, this build substitutes:

| LLD                         | This build                                              |
|------------------------------|-----------------------------------------------------------|
| AWS S3                      | Local disk storage behind a `Storage` interface (`app/services/storage.py`) — swapping in S3 later is a new class, not a rewrite. |
| HSM key management          | `cryptography.Fernet` encryption of PII fields (`mrn`, `ssn`) via `ENCRYPTION_KEY` (`app/core/encryption.py`). |
| RabbitMQ                    | Celery + Redis (same async task shape as LLD §2.8). |
| Full LOINC/NDC/ICD-10/SNOMED | ~20-25 seeded sample codes per system (`app/seed/taxonomy_seed.json`) — enough to demo validation/normalization, not the official code sets. |
| Tesseract OCR                | Not implemented. Text-extractable PDFs, plain text, and HL7v2 are supported; scanned/image documents are accepted but flagged (`is_scanned`, a quality warning) rather than silently producing empty output. |
| spaCy NLP                    | Not used; section segmentation is header-based regex (`app/services/preprocessing.py`). |
| Multi-region / HA / DR      | Single-instance Docker Compose stack only. |
| Epic/Cerner integration      | Not implemented (FHIR Bundle / HL7v2 export endpoints are provided as the integration surface). |

## Key flows implemented from the HLD/LLD

- Document upload → async Celery pipeline: preprocessing → Groq (or mock)
  extraction → validation/normalization against taxonomies → weighted
  confidence scoring (LLD §3 formula) → storage → audit log.
- Review UI: per-document confidence, validation errors/warnings, structured
  extraction view, JSON-based manual correction with reviewer attribution.
- Export: FHIR Bundle, HL7v2 (PID/OBR/OBX/RXE), CSV.
- RBAC: admin/clinician can upload & review; analyst is read/export only.
- Audit trail per document (upload, preprocessing, extraction, review,
  export, failure) surfaced in the UI.
- Dashboard KPIs: total/completed/failed documents, avg confidence
  ("accuracy"), avg/p95 processing time, error rate — from `/api/v1/metrics/summary`.
- Prometheus metrics (`documents_processed_total`, `documents_processing_duration_ms`,
  `extraction_confidence_score`, `validation_errors_total`) — emitted by the
  worker process; note that since the worker and backend are separate
  containers with separate Prometheus registries, worker-emitted metrics
  aren't visible on the backend's `/metrics` endpoint in this simplified
  setup (a real deployment would use a Pushgateway or multiprocess mode).
