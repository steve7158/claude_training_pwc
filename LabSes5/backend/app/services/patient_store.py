import json
from pathlib import Path

from app.models.schemas import Patient

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "patients.json"

_patients: dict[str, Patient] | None = None


def _load() -> dict[str, Patient]:
    global _patients
    if _patients is None:
        raw = json.loads(_DATA_PATH.read_text())
        _patients = {p["id"]: Patient(**p) for p in raw}
    return _patients


def list_patients() -> list[Patient]:
    return list(_load().values())


def get_patient(patient_id: str) -> Patient | None:
    return _load().get(patient_id)
