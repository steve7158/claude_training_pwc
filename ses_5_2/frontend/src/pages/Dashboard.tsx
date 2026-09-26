import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/client";
import type { DocumentOut, MetricsSummary } from "../api/types";
import KpiCard from "../components/KpiCard";
import StatusBadge from "../components/StatusBadge";

export default function Dashboard() {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [recent, setRecent] = useState<DocumentOut[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const [metricsRes, docsRes] = await Promise.all([api.getMetricsSummary(), api.listDocuments()]);
      setMetrics(metricsRes);
      setRecent(docsRes.items.slice(0, 8));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    }
  }

  useEffect(() => {
    load();
    const interval = setInterval(load, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
        <p className="text-sm text-slate-500">Clinical document extraction performance overview</p>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {metrics && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <KpiCard label="Documents processed" value={String(metrics.total_documents)} sublabel={`${metrics.documents_completed} completed`} />
          <KpiCard label="Accuracy (avg confidence)" value={`${metrics.accuracy_rate}%`} />
          <KpiCard label="Avg processing time" value={`${metrics.avg_processing_time_ms} ms`} sublabel={`p95: ${metrics.p95_latency_ms} ms`} />
          <KpiCard label="Error rate" value={`${metrics.error_rate}%`} sublabel={`${metrics.documents_failed} failed`} />
        </div>
      )}

      <div className="rounded-xl border border-slate-200 bg-white">
        <div className="flex items-center justify-between border-b border-slate-100 px-4 py-3">
          <h2 className="font-semibold text-slate-800">Recent documents</h2>
          <Link to="/documents" className="text-sm text-carta-600 hover:underline">
            View all
          </Link>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-slate-500">
            <tr>
              <th className="px-4 py-2">Filename</th>
              <th className="px-4 py-2">Type</th>
              <th className="px-4 py-2">Status</th>
              <th className="px-4 py-2">Uploaded</th>
            </tr>
          </thead>
          <tbody>
            {recent.map((doc) => (
              <tr key={doc.id} className="border-t border-slate-100 hover:bg-slate-50">
                <td className="px-4 py-2">
                  <Link to={`/documents/${doc.id}`} className="text-carta-600 hover:underline">
                    {doc.original_filename}
                  </Link>
                </td>
                <td className="px-4 py-2 text-slate-600">{doc.document_type.replaceAll("_", " ")}</td>
                <td className="px-4 py-2">
                  <StatusBadge status={doc.processing_status} />
                </td>
                <td className="px-4 py-2 text-slate-500">{new Date(doc.uploaded_at).toLocaleString()}</td>
              </tr>
            ))}
            {recent.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-center text-slate-400">
                  No documents uploaded yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
