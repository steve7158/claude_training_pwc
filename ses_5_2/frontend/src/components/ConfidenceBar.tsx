export default function ConfidenceBar({ score, label }: { score: number; label?: string }) {
  const pct = Math.round(score * 100);
  const color = pct >= 90 ? "bg-emerald-500" : pct >= 70 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="w-full">
      {label && (
        <div className="mb-1 flex justify-between text-xs text-slate-600">
          <span>{label}</span>
          <span className="font-medium">{pct}%</span>
        </div>
      )}
      <div className="h-2 w-full overflow-hidden rounded-full bg-slate-200">
        <div className={`h-full ${color}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
