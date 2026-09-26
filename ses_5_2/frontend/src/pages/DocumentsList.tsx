import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { DocumentOut, ProcessingStatus } from "../api/types";
import StatusBadge from "../components/StatusBadge";

const STATUS_OPTIONS: ProcessingStatus[] = ["received", "preprocessing", "processing", "completed", "failed"];

export default function DocumentsList() {
  const [documents, setDocuments] = useState<DocumentOut[]>([]);
  const [statusFilter, setStatusFilter] = useState<ProcessingStatus | "">("");
  const [total, setTotal] = useState(0);

  async function load() {
    const res = await api.listDocuments(statusFilter || undefined);
    setDocuments(res.items);
    setTotal(res.total);
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, [statusFilter]);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-slate-900">Documents ({total})</h1>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value as ProcessingStatus | "")}
          className="rounded-md border border-slate-300 px-3 py-1.5 text-sm"
        >
          <option value="">All statuses</option>
          {STATUS_OPTIONS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-2">Filename</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Source</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Uploaded by</th>
              <th className="px-4 py-2">Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {documents.map((doc) => (
              <tr key={doc.id} className="border-t border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-2">
                  <Link to={`/documents/${doc.id}`} className="text-carta-600 hover:underline">
                    {doc.original_filename}
                  </Link>
                </td>
                <td className="px-4 py-2 text-slate-600">{doc.document_type.replaceAll("_", " ")}</td>
                <td className="px-4 py-2 text-slate-600">{doc.source_system}</td>
                <td className="px-4 py-2">
                  <StatusBadge status={doc.processing_status} />
                </td>
                <td className="px-4 py-2 text-slate-500">{doc.created_by}</td>
                <td className="px-4 py-2 text-slate-500">{new Date(doc.uploaded_at).toLocaleString()}</td>
              </tr>
            ))}
            {documents.length === 0 && (
              <tr>
                <td colSpan={6} className="px-4 py-6 text-center text-slate-400">
                  No documents found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
