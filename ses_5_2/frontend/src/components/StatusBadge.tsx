import type { ProcessingStatus } from "../api/types";

const STYLES: Record<ProcessingStatus, string> = {
  received: "bg-slate-100 text-slate-700",
  preprocessing: "bg-amber-100 text-amber-800",
  processing: "bg-blue-100 text-blue-800",
  completed: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
};

export default function StatusBadge({ status }: { status: ProcessingStatus }) {
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${STYLES[status]}`}>
      {status}
    </span>
  );
}
