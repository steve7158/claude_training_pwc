export type Role = "admin" | "clinician" | "analyst";

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: Role;
}

export type DocumentType = "discharge_summary" | "lab_report" | "imaging" | "progress_note";

export type ProcessingStatus = "received" | "preprocessing" | "processing" | "completed" | "failed";

export interface DocumentOut {
  id: string;
  patient_id: string | null;
  document_type: DocumentType;
  source_system: string;
  original_filename: string;
  file_size: number;
  mime_type: string;
  uploaded_at: string;
  processing_status: ProcessingStatus;
  error_message: string | null;
  created_by: string;
}

export interface PatientDemographics {
  mrn: string | null;
  first_name: string;
  last_name: string;
  dob: string | null;
  gender: "M" | "F" | "O" | null;
  ssn: string | null;
}

export interface VitalSigns {
  temperature: number | null;
  temp_unit: "F" | "C" | null;
  blood_pressure: string | null;
  heart_rate: number | null;
  respiratory_rate: number | null;
  oxygen_saturation: number | null;
}

export interface LabResult {
  test_name: string;
  test_code: string | null;
  result_value: number;
  unit: string;
  reference_range: string | null;
  normal_range_low: number | null;
  normal_range_high: number | null;
  result_date: string | null;
  status: "normal" | "abnormal" | "critical" | "unknown";
}

export interface Medication {
  drug_name: string;
  ndc_code: string | null;
  route: string | null;
  frequency: string | null;
  dosage: string | null;
  start_date: string | null;
  end_date: string | null;
  indication: string | null;
}

export interface ClinicalExtraction {
  demographics: PatientDemographics;
  vitals: VitalSigns | null;
  chief_complaint: string | null;
  history_of_present_illness: string | null;
  medications: Medication[];
  allergies: string[];
  diagnoses: string[];
  procedures: string[];
  lab_results: LabResult[];
  assessment_and_plan: string | null;
  extraction_confidence: number;
  extraction_metadata: Record<string, unknown>;
}

export interface ValidationResultOut {
  is_valid: boolean;
  errors: string[];
  warnings: string[];
  confidence_score: number;
}

export interface ExtractionOut {
  document_id: string;
  extraction_status: string;
  extracted_data: ClinicalExtraction | null;
  validation_results: ValidationResultOut | null;
  confidence_score: number;
  processing_time_ms: number;
  reviewed_by: string | null;
  reviewed_at: string | null;
}

export interface AuditLogEntry {
  action: string;
  actor: string;
  detail: Record<string, unknown>;
  created_at: string;
}

export interface MetricsSummary {
  total_documents: number;
  status_counts: Record<string, number>;
  documents_completed: number;
  documents_failed: number;
  accuracy_rate: number;
  avg_processing_time_ms: number;
  p95_latency_ms: number;
  error_rate: number;
}
