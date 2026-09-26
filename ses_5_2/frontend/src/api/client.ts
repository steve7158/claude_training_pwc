import type {
  AuditLogEntry,
  ClinicalExtraction,
  DocumentOut,
  DocumentType,
  ExtractionOut,
  MetricsSummary,
  ProcessingStatus,
  User,
} from "./types";

const API_BASE = "/api/v1";
const TOKEN_KEY = "carta_token";

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(options.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail ?? detail;
    } catch {
      // ignore
    }
    throw new ApiError(res.status, typeof detail === "string" ? detail : JSON.stringify(detail));
  }
  const contentType = res.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    return res.json() as Promise<T>;
  }
  return (await res.text()) as unknown as T;
}

export const api = {
  async login(email: string, password: string) {
    const form = new URLSearchParams();
    form.set("username", email);
    form.set("password", password);
    return request<{ access_token: string; token_type: string; user: User }>("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form.toString(),
    });
  },

  async register(email: string, password: string, fullName: string, role: string) {
    return request<User>("/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName, role }),
    });
  },

  async me() {
    return request<User>("/auth/me");
  },

  async listDocuments(status?: ProcessingStatus) {
    const qs = status ? `?status=${status}` : "";
    return request<{ total: number; items: DocumentOut[] }>(`/documents${qs}`);
  },

  async getDocument(id: string) {
    return request<DocumentOut>(`/documents/${id}`);
  },

  async uploadDocument(file: File, documentType: DocumentType, sourceSystem: string, patientId?: string) {
    const form = new FormData();
    form.set("file", file);
    form.set("document_type", documentType);
    form.set("source_system", sourceSystem);
    if (patientId) form.set("patient_id", patientId);
    return request<{ document_id: string; status: string; processing_status: string }>("/documents/upload", {
      method: "POST",
      body: form,
    });
  },

  async getExtraction(documentId: string) {
    return request<ExtractionOut>(`/documents/${documentId}/extraction`);
  },

  async updateExtraction(documentId: string, extractedData: ClinicalExtraction) {
    return request<ExtractionOut>(`/documents/${documentId}/extraction`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ extracted_data: extractedData }),
    });
  },

  async getAuditTrail(documentId: string) {
    return request<AuditLogEntry[]>(`/documents/${documentId}/audit`);
  },

  async getMetricsSummary() {
    return request<MetricsSummary>("/metrics/summary");
  },

  // Auth is via an Authorization header, which a plain <a href> navigation
  // never sends - so exports are fetched here (with the header attached)
  // and handed to the browser as a Blob download instead.
  async downloadExport(documentId: string, format: "fhir" | "hl7" | "csv") {
    const token = getToken();
    const headers = new Headers();
    if (token) headers.set("Authorization", `Bearer ${token}`);

    const res = await fetch(`${API_BASE}/documents/${documentId}/export?format=${format}`, { headers });
    if (!res.ok) {
      throw new ApiError(res.status, await res.text());
    }
    const blob = await res.blob();
    const extension = format === "fhir" ? "json" : format === "hl7" ? "hl7" : "csv";
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `extraction_${documentId}.${extension}`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },
};

export { ApiError };
