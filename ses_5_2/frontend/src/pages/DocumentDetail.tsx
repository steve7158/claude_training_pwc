import { useCallback, useEffect, useState, type ReactNode } from "react";
import { useParams } from "react-router-dom";

import { api } from "../api/client";
import type { AuditLogEntry, ClinicalExtraction, DocumentOut, ExtractionOut } from "../api/types";
import AuditTimeline from "../components/AuditTimeline";
import ConfidenceBar from "../components/ConfidenceBar";
import StatusBadge from "../components/StatusBadge";
import { useAuth } from "../context/AuthContext";

const ACTIVE_STATUSES = new Set(["received", "preprocessing", "processing"]);

export default function DocumentDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();
  const [document, setDocument] = useState<DocumentOut | null>(null);
  const [extraction, setExtraction] = useState<ExtractionOut | null>(null);
  const [audit, setAudit] = useState<AuditLogEntry[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [editMode, setEditMode] = useState(false);
  const [jsonDraft, setJsonDraft] = useState("");
  const [saveError, setSaveError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const canEdit = user?.role === "admin" || user?.role === "clinician";

  const load = useCallback(async () => {
    if (!id) return;
    try {
      const [docRes, extRes, auditRes] = await Promise.all([
        api.getDocument(id),
        api.getExtraction(id),
        api.getAuditTrail(id),
      ]);
      setDocument(docRes);
      setExtraction(extRes);
      setAudit(auditRes);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load document");
    }
  }, [id]);

  useEffect(() => {
    load();
  }, [load]);

  useEffect(() => {
    if (!document || !ACTIVE_STATUSES.has(document.processing_status)) return;
    const interval = setInterval(load, 2000);
    return () => clearInterval(interval);
  }, [document, load]);

  function startEdit() {
    if (extraction?.extracted_data) {
      setJsonDraft(JSON.stringify(extraction.extracted_data, null, 2));
    }
    setEditMode(true);
    setSaveError(null);
  }

  async function saveEdit() {
    if (!id) return;
    setSaving(true);
    setSaveError(null);
    try {
      const parsed: ClinicalExtraction = JSON.parse(jsonDraft);
      const updated = await api.updateExtraction(id, parsed);
      setExtraction(updated);
      setEditMode(false);
      const auditRes = await api.getAuditTrail(id);
      setAudit(auditRes);
    } catch (err) {
      setSaveError(err instanceof Error ? err.message : "Failed to save");
    } finally {
      setSaving(false);
    }
  }

  if (error) return <p className="text-sm text-red-600">{error}</p>;
  if (!document) return <p className="text-sm text-slate-500">Loading...</p>;

  const data = extraction?.extracted_data;
  const validation = extraction?.validation_results;

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{document.original_filename}</h1>
          <p className="text-sm text-slate-500">
            {document.document_type.replaceAll("_", " ")} &middot; {document.source_system} &middot; uploaded by{" "}
            {document.created_by}
          </p>
        </div>
        <StatusBadge status={document.processing_status} />
      </div>

      {document.processing_status === "failed" && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">
          Processing failed: {document.error_message}
        </div>
      )}

      {ACTIVE_STATUSES.has(document.processing_status) && (
        <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 text-sm text-blue-700">
          Processing in progress ({document.processing_status})... this page updates automatically.
        </div>
      )}

      {data && (
        <>
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <ConfidenceBar score={extraction!.confidence_score} label="Overall confidence" />
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm">
              <div className="text-xs font-medium uppercase text-slate-500">Processing time</div>
              <div className="mt-1 text-lg font-semibold">{extraction!.processing_time_ms} ms</div>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4 text-sm">
              <div className="text-xs font-medium uppercase text-slate-500">Review status</div>
              <div className="mt-1">
                {extraction!.reviewed_by ? (
                  <span className="text-emerald-700">Reviewed by {extraction!.reviewed_by}</span>
                ) : (
                  <span className="text-slate-500">Not yet reviewed</span>
                )}
              </div>
            </div>
          </div>

          {validation && (validation.errors.length > 0 || validation.warnings.length > 0) && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm">
              {validation.errors.map((e, i) => (
                <p key={`err-${i}`} className="text-red-700">
                  ⚠ {e}
                </p>
              ))}
              {validation.warnings.map((w, i) => (
                <p key={`warn-${i}`} className="text-amber-700">
                  {w}
                </p>
              ))}
            </div>
          )}

          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-slate-800">Extracted Data</h2>
            <div className="flex gap-2">
              <button
                onClick={() => api.downloadExport(document.id, "fhir")}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
              >
                Export FHIR
              </button>
              <button
                onClick={() => api.downloadExport(document.id, "hl7")}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
              >
                Export HL7
              </button>
              <button
                onClick={() => api.downloadExport(document.id, "csv")}
                className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
              >
                Export CSV
              </button>
              {canEdit && !editMode && (
                <button
                  onClick={startEdit}
                  className="rounded-md bg-carta-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-carta-700"
                >
                  Edit & Review
                </button>
              )}
            </div>
          </div>

          {editMode ? (
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <p className="mb-2 text-xs text-slate-500">
                Edit the structured extraction JSON below, then save to persist your corrections and mark this
                extraction as reviewed.
              </p>
              <textarea
                value={jsonDraft}
                onChange={(e) => setJsonDraft(e.target.value)}
                rows={20}
                className="w-full rounded-md border border-slate-300 p-3 font-mono text-xs"
              />
              {saveError && <p className="mt-2 text-sm text-red-600">{saveError}</p>}
              <div className="mt-3 flex gap-2">
                <button
                  onClick={saveEdit}
                  disabled={saving}
                  className="rounded-md bg-carta-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-carta-700 disabled:opacity-50"
                >
                  {saving ? "Saving..." : "Save & Mark Reviewed"}
                </button>
                <button
                  onClick={() => setEditMode(false)}
                  className="rounded-md border border-slate-300 px-3 py-1.5 text-sm hover:bg-slate-100"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
              <Section title="Demographics">
                <KeyValue label="Name" value={`${data.demographics.first_name} ${data.demographics.last_name}`} />
                <KeyValue label="MRN" value={data.demographics.mrn ?? "—"} />
                <KeyValue label="DOB" value={data.demographics.dob ?? "—"} />
                <KeyValue label="Gender" value={data.demographics.gender ?? "—"} />
              </Section>

              <Section title="Vitals">
                {data.vitals ? (
                  <>
                    <KeyValue label="Temperature" value={data.vitals.temperature ? `${data.vitals.temperature}°${data.vitals.temp_unit ?? ""}` : "—"} />
                    <KeyValue label="Blood pressure" value={data.vitals.blood_pressure ?? "—"} />
                    <KeyValue label="Heart rate" value={data.vitals.heart_rate ? String(data.vitals.heart_rate) : "—"} />
                    <KeyValue label="SpO2" value={data.vitals.oxygen_saturation ? `${data.vitals.oxygen_saturation}%` : "—"} />
                  </>
                ) : (
                  <p className="text-sm text-slate-400">No vitals extracted</p>
                )}
              </Section>

              <Section title="Chief Complaint & HPI">
                <p className="text-sm text-slate-700">{data.chief_complaint || "—"}</p>
                {data.history_of_present_illness && (
                  <p className="mt-2 text-sm text-slate-600">{data.history_of_present_illness}</p>
                )}
              </Section>

              <Section title="Assessment & Plan">
                <p className="text-sm text-slate-700">{data.assessment_and_plan || "—"}</p>
              </Section>

              <Section title={`Lab Results (${data.lab_results.length})`}>
                {data.lab_results.length === 0 ? (
                  <p className="text-sm text-slate-400">None extracted</p>
                ) : (
                  <table className="w-full text-left text-xs">
                    <thead className="text-slate-500">
                      <tr>
                        <th className="py-1">Test</th>
                        <th className="py-1">Value</th>
                        <th className="py-1">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.lab_results.map((lab, i) => (
                        <tr key={i} className="border-t border-slate-100">
                          <td className="py-1">
                            {lab.test_name} {lab.test_code && <span className="text-slate-400">({lab.test_code})</span>}
                          </td>
                          <td className="py-1">
                            {lab.result_value} {lab.unit}
                          </td>
                          <td className="py-1">
                            <span
                              className={
                                lab.status === "abnormal" || lab.status === "critical"
                                  ? "text-red-600"
                                  : lab.status === "normal"
                                    ? "text-emerald-600"
                                    : "text-slate-400"
                              }
                            >
                              {lab.status}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </Section>

              <Section title={`Medications (${data.medications.length})`}>
                {data.medications.length === 0 ? (
                  <p className="text-sm text-slate-400">None extracted</p>
                ) : (
                  <ul className="space-y-1 text-sm text-slate-700">
                    {data.medications.map((med, i) => (
                      <li key={i}>
                        <span className="font-medium">{med.drug_name}</span>{" "}
                        <span className="text-slate-500">
                          {[med.dosage, med.route, med.frequency].filter(Boolean).join(" · ")}
                        </span>
                      </li>
                    ))}
                  </ul>
                )}
              </Section>

              <Section title={`Diagnoses (${data.diagnoses.length})`}>
                <ListOrEmpty items={data.diagnoses} />
              </Section>

              <Section title={`Allergies (${data.allergies.length})`}>
                <ListOrEmpty items={data.allergies} />
              </Section>
            </div>
          )}
        </>
      )}

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <h2 className="mb-3 text-lg font-semibold text-slate-800">Audit Trail</h2>
        <AuditTimeline entries={audit} />
      </div>
    </div>
  );
}

function Section({ title, children }: { title: string; children: ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <h3 className="mb-2 text-sm font-semibold text-slate-700">{title}</h3>
      {children}
    </div>
  );
}

function KeyValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between border-b border-slate-50 py-1 text-sm last:border-0">
      <span className="text-slate-500">{label}</span>
      <span className="font-medium text-slate-800">{value}</span>
    </div>
  );
}

function ListOrEmpty({ items }: { items: string[] }) {
  if (items.length === 0) return <p className="text-sm text-slate-400">None extracted</p>;
  return (
    <ul className="list-inside list-disc space-y-1 text-sm text-slate-700">
      {items.map((item, i) => (
        <li key={i}>{item}</li>
      ))}
    </ul>
  );
}
