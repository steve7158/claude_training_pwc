from fastapi import APIRouter, HTTPException

from app.models.schemas import DraftNoteRequest, DraftNoteResponse
from app.services import patient_store
from app.services.llm_client import LLMError, complete
from app.services.prompts import build_draft_note_prompt

router = APIRouter(prefix="/api/patients", tags=["notes"])


@router.post("/{patient_id}/draft-note", response_model=DraftNoteResponse)
async def draft_note(patient_id: str, body: DraftNoteRequest):
    patient = patient_store.get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"No patient with id '{patient_id}'")
    if not body.raw_text.strip():
        raise HTTPException(status_code=400, detail="raw_text must not be empty")

    prompt = build_draft_note_prompt(patient, body.raw_text)
    try:
        draft = await complete(prompt)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return DraftNoteResponse(patient_id=patient_id, draft_note=draft)
