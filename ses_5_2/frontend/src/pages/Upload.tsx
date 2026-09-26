import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";

import { api } from "../api/client";
import type { DocumentType } from "../api/types";

const DOCUMENT_TYPES: { value: DocumentType; label: string }[] = [
  { value: "discharge_summary", label: "Discharge Summary" },
  { value: "lab_report", label: "Lab Report" },
  { value: "imaging", label: "Imaging Report" },
  { value: "progress_note", label: "Progress Note" },
];

export default function Upload() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [documentType, setDocumentType] = useState<DocumentType>("progress_note");
  const [sourceSystem, setSourceSystem] = useState("manual-upload");
  const [patientId, setPatientId] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [dragOver, setDragOver] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Please choose a file to upload.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const res = await api.uploadDocument(file, documentType, sourceSystem, patientId || undefined);
      navigate(`/documents/${res.document_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold text-slate-900">Upload Document</h1>
      <p className="mt-1 text-sm text-slate-500">
        Supported: text-extractable PDFs, plain text, and HL7v2 messages. Scanned images are accepted but flagged
        (OCR is not enabled in this deployment).
      </p>

      <form onSubmit={handleSubmit} className="mt-6 space-y-4 rounded-xl border border-slate-200 bg-white p-6">
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setDragOver(true);
          }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => {
            e.preventDefault();
            setDragOver(false);
            const dropped = e.dataTransfer.files?.[0];
            if (dropped) setFile(dropped);
          }}
          className={`rounded-lg border-2 border-dashed p-8 text-center text-sm ${
            dragOver ? "border-carta-500 bg-carta-50" : "border-slate-300"
          }`}
        >
          {file ? (
            <p className="text-slate-700">{file.name}</p>
          ) : (
            <p className="text-slate-500">Drag & drop a file here, or</p>
          )}
          <label className="mt-2 inline-block cursor-pointer text-carta-600 hover:underline">
            browse
            <input
              type="file"
              className="hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Document type</label>
          <select
            value={documentType}
            onChange={(e) => setDocumentType(e.target.value as DocumentType)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          >
            {DOCUMENT_TYPES.map((dt) => (
              <option key={dt.value} value={dt.value}>
                {dt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Source system</label>
          <input
            value={sourceSystem}
            onChange={(e) => setSourceSystem(e.target.value)}
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-700">Patient ID (optional, UUID)</label>
          <input
            value={patientId}
            onChange={(e) => setPatientId(e.target.value)}
            placeholder="leave blank if unknown"
            className="mt-1 w-full rounded-md border border-slate-300 px-3 py-2 text-sm"
          />
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        <button
          type="submit"
          disabled={submitting}
          className="w-full rounded-md bg-carta-600 px-3 py-2 text-sm font-medium text-white hover:bg-carta-700 disabled:opacity-50"
        >
          {submitting ? "Uploading..." : "Upload & Process"}
        </button>
      </form>
    </div>
  );
}
