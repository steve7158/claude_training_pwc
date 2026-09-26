from typing import Optional

from pydantic import BaseModel


class VisitNote(BaseModel):
    date: str
    note: str


class Patient(BaseModel):
    id: str
    name: str
    age: int
    sex: str
    problem_list: list[str]
    medications: list[str]
    allergies: list[str]
    vitals: dict[str, str]
    visit_history: list[VisitNote]


class PatientSummary(BaseModel):
    id: str
    name: str
    age: int
    sex: str


class SummarizeResponse(BaseModel):
    patient_id: str
    summary: str


class DraftNoteRequest(BaseModel):
    raw_text: str


class DraftNoteResponse(BaseModel):
    patient_id: str
    draft_note: str


class ErrorResponse(BaseModel):
    detail: str
    hint: Optional[str] = None
