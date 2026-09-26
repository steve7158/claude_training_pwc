async function request(path, options) {
  const res = await fetch(`/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json();
}

export function listPatients() {
  return request("/patients");
}

export function getPatient(id) {
  return request(`/patients/${id}`);
}

export function summarizePatient(id) {
  return request(`/patients/${id}/summarize`, { method: "POST" });
}

export function draftNote(id, rawText) {
  return request(`/patients/${id}/draft-note`, {
    method: "POST",
    body: JSON.stringify({ raw_text: rawText }),
  });
}
