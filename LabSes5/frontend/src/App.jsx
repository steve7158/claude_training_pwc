import { useEffect, useState } from "react";

import { getPatient, listPatients } from "./api.js";
import NoteDrafter from "./components/NoteDrafter.jsx";
import PatientChart from "./components/PatientChart.jsx";
import PatientList from "./components/PatientList.jsx";

export default function App() {
  const [patients, setPatients] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [patient, setPatient] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    listPatients()
      .then((data) => {
        setPatients(data);
        if (data.length > 0) setSelectedId(data[0].id);
      })
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => {
    if (!selectedId) return;
    getPatient(selectedId)
      .then(setPatient)
      .catch((err) => setError(err.message));
  }, [selectedId]);

  return (
    <div className="app">
      <header>
        <h1>Banner Health — Clinical Documentation Assistant</h1>
        <p className="disclaimer">
          Prototype only. All patient data is synthetic (fabricated for demo purposes) — no real
          PHI is used or stored.
        </p>
      </header>

      {error && <p className="error">{error}</p>}

      <main>
        <PatientList patients={patients} selectedId={selectedId} onSelect={setSelectedId} />
        {patient && (
          <div className="workspace">
            <PatientChart patient={patient} />
            <NoteDrafter patientId={patient.id} />
          </div>
        )}
      </main>
    </div>
  );
}
