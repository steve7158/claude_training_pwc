export default function PatientList({ patients, selectedId, onSelect }) {
  return (
    <div className="patient-list">
      <h2>Patients</h2>
      <ul>
        {patients.map((p) => (
          <li key={p.id}>
            <button
              className={p.id === selectedId ? "selected" : ""}
              onClick={() => onSelect(p.id)}
            >
              {p.name} <span className="meta">({p.age}, {p.sex})</span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
