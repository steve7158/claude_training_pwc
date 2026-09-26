"""Encrypts/decrypts the PII fields (mrn, ssn) of a ClinicalExtraction dict
before it is persisted to / read from the `extractions.data` JSON column.
See core/encryption.py for the underlying Fernet-based encryption.
"""
from app.core.encryption import decrypt_value, encrypt_value

PII_FIELDS = ("mrn", "ssn")


def encrypt_extraction_dict(data: dict) -> dict:
    demographics = dict(data.get("demographics") or {})
    for field in PII_FIELDS:
        if demographics.get(field):
            demographics[field] = encrypt_value(demographics[field])
    data = dict(data)
    data["demographics"] = demographics
    return data


def decrypt_extraction_dict(data: dict) -> dict:
    demographics = dict(data.get("demographics") or {})
    for field in PII_FIELDS:
        if demographics.get(field):
            demographics[field] = decrypt_value(demographics[field])
    data = dict(data)
    data["demographics"] = demographics
    return data
