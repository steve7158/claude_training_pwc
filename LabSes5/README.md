# Banner Health — AI Clinical Documentation Assistant (Prototype)

An AI assistant that helps reduce physician documentation burden by:
1. **Summarizing** a patient's chart into a concise clinical brief.
2. **Drafting** a structured SOAP note from a physician's raw encounter notes.

## Status: prototype

- All patient data is **synthetic/fabricated** — no real PHI is used or stored.
- **Standalone** — no EHR integration.
- LLM calls go through **OpenRouter**, using a free-tier model, so no paid API key is required.

## Stack

- `backend/` — Python (FastAPI) API + LLM orchestration
- `frontend/` — Node.js (Express) UI server serving a React (Vite) app

## Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env and add your OpenRouter API key (free tier: https://openrouter.ai/keys)
uvicorn app.main:app --reload
```

Free-tier models on OpenRouter rotate and are shared across many users, so they can be
temporarily rate-limited or unavailable (the app surfaces this as a clear error in the UI —
just wait a bit and retry, or pick a different model). See currently available free models at
https://openrouter.ai/models?max_price=0 and set `OPENROUTER_MODEL` in `.env` accordingly.

Backend runs at `http://localhost:8000`.

### Frontend (development)

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`, proxying `/api` requests to the backend.

### Frontend (production-style)

```bash
cd frontend
npm install
npm run build
npm start
```

Serves the built app via the Express UI server at `http://localhost:3000`, proxying `/api` to the backend.

## API

| Method | Path | Description |
|---|---|---|
| GET | `/api/patients` | List synthetic patients |
| GET | `/api/patients/{id}` | Get a patient's full chart |
| POST | `/api/patients/{id}/summarize` | AI-generated chart summary |
| POST | `/api/patients/{id}/draft-note` | AI-drafted SOAP note from `{ raw_text }` |

## Out of scope (future work)

- Authentication/authorization, audit logging
- Real EHR integration (Epic/Cerner FHIR APIs)
- Persisting drafted notes back to a chart
- Compliance hardening for real PHI (BAA agreements, encryption at rest, etc.)
