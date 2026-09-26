from fastapi.testclient import TestClient

from app.main import app

CLINICAL_NOTE = """
Patient: Doe, Jane
MRN: MRN98765
DOB: 03/14/1980

Chief Complaint: Follow-up for type 2 diabetes.

Laboratory Results:
Glucose 118 mg/dL

Medications:
metformin 500mg oral twice daily

Diagnoses:
E11.9 Type 2 diabetes mellitus without complications
""".strip()


def _register_and_login(client: TestClient, role: str = "clinician") -> str:
    email = f"{role}-smoke@example.com"
    client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "full_name": "Smoke Test", "role": role},
    )
    resp = client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": "TestPass123!"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def test_health():
    with TestClient(app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200


def test_upload_and_extraction_pipeline_end_to_end():
    with TestClient(app) as client:
        token = _register_and_login(client)
        headers = {"Authorization": f"Bearer {token}"}

        files = {"file": ("note.txt", CLINICAL_NOTE.encode(), "text/plain")}
        data = {"document_type": "progress_note", "source_system": "smoke-test"}
        upload_resp = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
        assert upload_resp.status_code == 202, upload_resp.text
        document_id = upload_resp.json()["document_id"]

        # Celery is in eager mode (see conftest) so processing has already completed synchronously.
        doc_resp = client.get(f"/api/v1/documents/{document_id}", headers=headers)
        assert doc_resp.status_code == 200
        assert doc_resp.json()["processing_status"] == "completed"

        extraction_resp = client.get(f"/api/v1/documents/{document_id}/extraction", headers=headers)
        assert extraction_resp.status_code == 200
        body = extraction_resp.json()
        assert body["extraction_status"] == "completed"
        assert body["extracted_data"]["demographics"]["mrn"] == "MRN98765"

        export_resp = client.get(f"/api/v1/documents/{document_id}/export?format=fhir", headers=headers)
        assert export_resp.status_code == 200
        assert export_resp.json()["resourceType"] == "Bundle"

        audit_resp = client.get(f"/api/v1/documents/{document_id}/audit", headers=headers)
        assert audit_resp.status_code == 200
        actions = [entry["action"] for entry in audit_resp.json()]
        assert "document_uploaded" in actions
        assert "processing_completed" in actions


def test_analyst_cannot_upload():
    with TestClient(app) as client:
        token = _register_and_login(client, role="analyst")
        headers = {"Authorization": f"Bearer {token}"}
        files = {"file": ("note.txt", CLINICAL_NOTE.encode(), "text/plain")}
        data = {"document_type": "progress_note", "source_system": "smoke-test"}
        resp = client.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
        assert resp.status_code == 403
