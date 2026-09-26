"""Idempotent seed: demo users (one per role) + a small sample taxonomy
dataset (LOINC/NDC/ICD-10/SNOMED) - not the full official code sets, see
plan/README for the scoping rationale."""
import json
import logging
import os

from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.taxonomy import Icd10Code, LoincCode, NdcDrug, SnomedCode
from app.models.user import Role, User

logger = logging.getLogger(__name__)

_TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "taxonomy_seed.json")

DEMO_USERS = [
    {"email": "admin@carta.health", "password": "AdminPass123!", "full_name": "Ada Admin", "role": Role.admin},
    {"email": "clinician@carta.health", "password": "ClinicianPass123!", "full_name": "Cara Clinician", "role": Role.clinician},
    {"email": "analyst@carta.health", "password": "AnalystPass123!", "full_name": "Alex Analyst", "role": Role.analyst},
]


def _seed_users(db):
    for spec in DEMO_USERS:
        if db.query(User).filter(User.email == spec["email"]).first():
            continue
        db.add(
            User(
                email=spec["email"],
                hashed_password=hash_password(spec["password"]),
                full_name=spec["full_name"],
                role=spec["role"],
            )
        )
    db.commit()


def _seed_taxonomy(db):
    if db.query(LoincCode).count() > 0:
        return
    with open(_TAXONOMY_PATH) as f:
        data = json.load(f)

    for row in data["loinc"]:
        db.add(LoincCode(**row))
    for row in data["ndc"]:
        db.add(NdcDrug(**row))
    for row in data["icd10"]:
        db.add(Icd10Code(**row))
    for row in data["snomed"]:
        db.add(SnomedCode(**row))
    db.commit()


def seed_all():
    db = SessionLocal()
    try:
        _seed_users(db)
        _seed_taxonomy(db)
        logger.info("Seed data ensured (users + taxonomy).")
    finally:
        db.close()
