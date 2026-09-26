import { useState } from "react";

import { summarizePatient } from "../api.js";

export default function PatientChart({ patient }) {
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSummarize() {
    setLoading(true);
    setError("");
    setSummary("");
    try {
      const res = await summarizePatient(patient.id);
      setSummary(res.summary);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="patient-chart">
      <h2>{patient.name}</h2>
      <p className="meta">{patient.age} y/o {patient.sex}</p>

      <section>
        <h3>Problem list</h3>
        <ul>{patient.problem_list.map((p) => <li key={p}>{p}</li>)}</ul>
      </section>

      <section>
        <h3>Medications</h3>
        <ul>{patient.medications.map((m) => <li key={m}>{m}</li>)}</ul>
      </section>

      <section>
        <h3>Allergies</h3>
        <ul>{patient.allergies.map((a) => <li key={a}>{a}</li>)}</ul>
      </section>

      <section>
        <h3>Vitals / labs</h3>
        <ul>
          {Object.entries(patient.vitals).map(([k, v]) => (
            <li key={k}>{k}: {v}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>Visit history</h3>
        <ul className="visit-history">
          {patient.visit_history.map((v) => (
            <li key={v.date}><strong>{v.date}</strong>: {v.note}</li>
          ))}
        </ul>
      </section>

      <section>
        <h3>AI chart summary</h3>
        <button onClick={handleSummarize} disabled={loading}>
          {loading ? "Summarizing..." : "Summarize chart"}
        </button>
        {error && <p className="error">{error}</p>}
        {summary && <p className="summary">{summary}</p>}
      </section>
    </div>
  );
}
