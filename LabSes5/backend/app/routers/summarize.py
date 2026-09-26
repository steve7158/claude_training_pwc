from fastapi import APIRouter, HTTPException

from app.models.schemas import SummarizeResponse
from app.services import patient_store
from app.services.llm_client import LLMError, complete
from app.services.prompts import build_summarize_prompt

router = APIRouter(prefix="/api/patients", tags=["summarize"])


@router.post("/{patient_id}/summarize", response_model=SummarizeResponse)
async def summarize_patient(patient_id: str):
    patient = patient_store.get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"No patient with id '{patient_id}'")

    prompt = build_summarize_prompt(patient)
    try:
        summary = await complete(prompt)
    except LLMError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return SummarizeResponse(patient_id=patient_id, summary=summary)
