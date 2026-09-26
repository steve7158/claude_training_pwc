from fastapi import APIRouter, HTTPException

from app.models.schemas import Patient, PatientSummary
from app.services import patient_store

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("", response_model=list[PatientSummary])
def list_patients():
    return [
        PatientSummary(id=p.id, name=p.name, age=p.age, sex=p.sex)
        for p in patient_store.list_patients()
    ]


@router.get("/{patient_id}", response_model=Patient)
def get_patient(patient_id: str):
    patient = patient_store.get_patient(patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail=f"No patient with id '{patient_id}'")
    return patient
