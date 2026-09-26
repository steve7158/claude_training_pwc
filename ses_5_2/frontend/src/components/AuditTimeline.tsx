import type { AuditLogEntry } from "../api/types";

export default function AuditTimeline({ entries }: { entries: AuditLogEntry[] }) {
  if (entries.length === 0) {
    return <p className="text-sm text-slate-500">No audit events yet.</p>;
  }

  return (
    <ol className="space-y-3">
      {entries.map((entry, idx) => (
        <li key={idx} className="flex gap-3 text-sm">
          <div className="mt-1 h-2 w-2 flex-shrink-0 rounded-full bg-carta-500" />
          <div>
            <div className="font-medium text-slate-800">{entry.action.replaceAll("_", " ")}</div>
            <div className="text-xs text-slate-500">
              {entry.actor} &middot; {new Date(entry.created_at).toLocaleString()}
            </div>
            {Object.keys(entry.detail).length > 0 && (
              <pre className="mt-1 max-w-md whitespace-pre-wrap rounded bg-slate-50 p-1.5 text-[11px] text-slate-600">
                {JSON.stringify(entry.detail)}
              </pre>
            )}
          </div>
        </li>
      ))}
    </ol>
  );
}
