# Carta Healthcare: 66% Faster Clinical Data Processing

## Low-Level Design (LLD)
 
### 1. Technology Stack

- **Backend**: Python 3.11 with FastAPI

- **AI/LLM**: Claude API (claude-opus-5-5) with vision capability

- **Document Processing**: PyPDF2, Tesseract OCR, Poppler

- **Database**: PostgreSQL + Redis

- **Message Queue**: RabbitMQ for async processing

- **Object Storage**: AWS S3 for document storage

- **NLP**: spaCy for clinical NLP tasks

- **Data Validation**: Pydantic schemas

- **Security**: TLS 1.3, AES-256 encryption, HSM for key management
 
### 2. Detailed Component Architecture
 
#### 2.1 Document Ingestion Service
 
**API Endpoint**:

```python

POST /api/v1/documents/upload

Content-Type: multipart/form-data

Parameters:

  - file: document file (PDF, HL7, CDA, Image)

  - document_type: enum (discharge_summary, lab_report, imaging, progress_note)

  - patient_id: optional uuid

  - source_system: string

Response: {

  "document_id": "uuid",

  "status": "received",

  "processing_status": "queued",

  "estimated_completion": "timestamp"

}

```
 
**Database Schema**:

```sql

CREATE TABLE documents (

  id UUID PRIMARY KEY,

  patient_id UUID,

  document_type VARCHAR,

  source_system VARCHAR,

  original_filename VARCHAR,

  s3_path VARCHAR,

  file_size INT,

  mime_type VARCHAR,

  uploaded_at TIMESTAMP,

  processing_status ENUM('received', 'preprocessing', 'processing', 'completed', 'failed'),

  error_message TEXT,

  created_by VARCHAR

);
 
CREATE TABLE document_pages (

  id UUID PRIMARY KEY,

  document_id UUID REFERENCES documents(id),

  page_number INT,

  s3_path VARCHAR,

  ocr_text TEXT,

  confidence_score FLOAT

);

```
 
#### 2.2 Document Preprocessing Pipeline
 
**Preprocessing Flow**:

```python

def preprocess_document(document_id):

  doc = get_document(document_id)

  # Step 1: Format detection and conversion

  if doc.mime_type == 'application/pdf':

    text, images = extract_pdf(doc.s3_path)

  elif doc.mime_type.startswith('image/'):

    images = load_image(doc.s3_path)

    text = ""

  elif doc.mime_type == 'application/hl7':

    text = parse_hl7(doc.s3_path)

    images = []

  # Step 2: OCR for scanned documents

  if contains_scanned_pages(doc):

    for page_image in images:

      ocr_result = run_ocr(page_image)

      store_ocr_result(document_id, page_number, ocr_result)

  # Step 3: Text normalization

  normalized_text = normalize_text(text)

  # Step 4: Segment document

  sections = segment_document(normalized_text)

  return normalized_text, sections

```
 
**Quality Assessment**:

```json

{

  "quality_score": 0.95,

  "is_scanned": false,

  "has_structured_elements": true,

  "page_count": 3,

  "confidence_score": 0.92,

  "warnings": []

}

```
 
#### 2.3 Data Extraction Schema
 
**Pydantic Model**:

```python

class PatientDemographics(BaseModel):

  mrn: Optional[str]

  first_name: str

  last_name: str

  dob: date

  gender: Literal['M', 'F', 'O']

  ssn: Optional[str]
 
class VitalSigns(BaseModel):

  temperature: Optional[float]

  temp_unit: Literal['F', 'C']

  blood_pressure: Optional[str]  # "systolic/diastolic"

  heart_rate: Optional[int]

  respiratory_rate: Optional[int]

  oxygen_saturation: Optional[float]
 
class LabResult(BaseModel):

  test_name: str

  test_code: Optional[str]  # LOINC code

  result_value: float

  unit: str

  reference_range: Optional[str]

  normal_range_low: Optional[float]

  normal_range_high: Optional[float]

  result_date: datetime

  status: Literal['normal', 'abnormal', 'critical']
 
class Medication(BaseModel):

  drug_name: str

  ndc_code: Optional[str]

  route: str

  frequency: str

  dosage: str

  start_date: Optional[date]

  end_date: Optional[date]

  indication: Optional[str]
 
class ClinicalExtraction(BaseModel):

  demographics: PatientDemographics

  vitals: Optional[VitalSigns]

  chief_complaint: Optional[str]

  history_of_present_illness: Optional[str]

  medications: List[Medication]

  allergies: List[str]

  diagnoses: List[str]

  procedures: List[str]

  lab_results: List[LabResult]

  assessment_and_plan: Optional[str]

  extraction_confidence: float

  extraction_metadata: Dict

```
 
#### 2.4 LLM-Powered Extraction
 
**Claude API Integration**:

```python

def extract_clinical_data(document_id, normalized_text):

  doc = get_document(document_id)

  # Prepare context based on document type

  extraction_prompt = get_extraction_prompt(doc.document_type)

  # Call Claude with document content

  response = client.messages.create(

    model="claude-opus-5-5",

    max_tokens=4096,

    system="""You are a clinical data extraction expert. 

              Extract all clinical information from the document.

              Return structured JSON matching the provided schema.""",

    messages=[{

      "role": "user",

      "content": [

        {

          "type": "text",

          "text": extraction_prompt

        },

        {

          "type": "text",

          "text": f"Document content:\n{normalized_text[:50000]}"

        }

      ]

    }]

  )

  # Parse and validate response

  extracted_data = parse_response(response.content)

  validated_data = validate_extraction(extracted_data)

  return validated_data

```
 
#### 2.5 Data Validation & Normalization
 
**Validation Workflow**:

```python

def validate_and_normalize(extracted_data):

  validation_results = {

    "is_valid": True,

    "errors": [],

    "warnings": [],

    "confidence_score": 1.0

  }

  # Validate demographics

  if not is_valid_mrn(extracted_data.demographics.mrn):

    validation_results["errors"].append("Invalid MRN format")

    validation_results["is_valid"] = False

  # Validate clinical codes

  for lab in extracted_data.lab_results:

    if lab.test_code:

      if not loinc_db.exists(lab.test_code):

        validation_results["warnings"].append(

          f"Unknown LOINC code: {lab.test_code}"

        )

      lab.test_code = loinc_db.normalize(lab.test_code)

  # Normalize medications

  for med in extracted_data.medications:

    if med.ndc_code:

      ndc_normalized = ndc_db.normalize(med.ndc_code)

      med.ndc_code = ndc_normalized

      med.drug_name = ndc_db.get_generic_name(ndc_normalized)

  # Validate value ranges

  for lab in extracted_data.lab_results:

    normal_range = get_normal_range(lab.test_code, lab.unit)

    if normal_range:

      if lab.result_value < normal_range.low:

        lab.status = "abnormal"

      elif lab.result_value > normal_range.high:

        lab.status = "abnormal"

      else:

        lab.status = "normal"

  # Calculate overall confidence

  validation_results["confidence_score"] = calculate_confidence(

    extracted_data,

    validation_results

  )

  return extracted_data, validation_results

```
 
#### 2.6 Reference Data & Taxonomy
 
**Database Tables**:

```sql

-- LOINC codes

CREATE TABLE loinc_codes (

  loinc_code VARCHAR(10) PRIMARY KEY,

  test_name VARCHAR,

  short_name VARCHAR,

  component VARCHAR,

  property VARCHAR,

  time_aspect VARCHAR,

  system VARCHAR,

  scale_type VARCHAR,

  method_type VARCHAR,

  normal_range_low FLOAT,

  normal_range_high FLOAT,

  unit VARCHAR

);
 
-- NDC (National Drug Code)

CREATE TABLE ndc_drugs (

  ndc_code VARCHAR(11) PRIMARY KEY,

  generic_name VARCHAR,

  brand_name VARCHAR,

  strength VARCHAR,

  unit_dose_form VARCHAR,

  route VARCHAR,

  manufacturer VARCHAR,

  gi_division_status VARCHAR

);
 
-- ICD-10 Diagnosis Codes

CREATE TABLE icd10_codes (

  code VARCHAR(10) PRIMARY KEY,

  description TEXT,

  short_description VARCHAR,

  category VARCHAR

);
 
-- SNOMED-CT Codes

CREATE TABLE snomed_codes (

  snomed_id VARCHAR PRIMARY KEY,

  preferred_term VARCHAR,

  hierarchy TEXT

);

```
 
#### 2.7 Output Generation
 
**API Endpoints**:

```

GET /api/v1/documents/{document_id}/extraction

Response: {

  "document_id": "uuid",

  "extraction_status": "completed",

  "extracted_data": ClinicalExtraction,

  "validation_results": {...},

  "confidence_score": 0.96,

  "processing_time_ms": 2450

}
 
GET /api/v1/documents/{document_id}/export?format=fhir

Response: FHIR Bundle JSON
 
GET /api/v1/documents/{document_id}/export?format=hl7

Response: HL7v2 message
 
POST /api/v1/documents/{document_id}/validate

Body: { "extracted_data": {...} }

Response: { "is_valid": true, "errors": [], "warnings": [] }

```
 
**Output Formats**:
 
FHIR Bundle:

```json

{

  "resourceType": "Bundle",

  "type": "transaction",

  "entry": [

    {

      "resource": {

        "resourceType": "Patient",

        "id": "uuid",

        "name": [{"given": ["John"], "family": "Doe"}],

        "birthDate": "1970-01-01"

      }

    },

    {

      "resource": {

        "resourceType": "Observation",

        "code": {"coding": [{"system": "http://loinc.org", "code": "2085-9"}]},

        "valueQuantity": {"value": 100, "unit": "mg/dL"}

      }

    }

  ]

}

```
 
#### 2.8 Processing Queue & Async Jobs
 
**Celery Task Definition**:

```python

@celery_app.task(bind=True, max_retries=3)

def process_document_task(self, document_id):

  try:

    # Preprocessing

    update_status(document_id, 'preprocessing')

    text, sections = preprocess_document(document_id)

    # Extraction

    update_status(document_id, 'processing')

    extraction = extract_clinical_data(document_id, text)

    # Validation

    extraction, validation = validate_and_normalize(extraction)

    # Storage

    store_extraction(document_id, extraction, validation)

    # Generate output

    generate_outputs(document_id, extraction)

    update_status(document_id, 'completed')

  except Exception as exc:

    self.retry(exc=exc, countdown=60)

```
 
### 3. Confidence Scoring Algorithm
 
```python

def calculate_confidence(extraction, validation):

  scores = {}

  # Field-level confidence

  scores['demographics'] = 0.98 if validation.errors else 0.95

  scores['vitals'] = extract_ocr_confidence(extraction.vitals)

  scores['lab_results'] = validate_lab_confidence(extraction.lab_results)

  scores['medications'] = validate_med_confidence(extraction.medications)

  # Normalize unknown fields (reduce confidence)

  unknown_count = len([w for w in validation.warnings 

                       if 'unknown' in w.lower()])

  unknown_penalty = unknown_count * 0.02

  # Overall confidence

  overall = (

    (scores['demographics'] * 0.25) +

    (scores['vitals'] * 0.15) +

    (scores['lab_results'] * 0.35) +

    (scores['medications'] * 0.25) -

    unknown_penalty

  )

  return max(0, min(1, overall))

```
 
### 4. Error Handling & Retry Logic
 
**Error Types**:

```python

class DocumentProcessingError(Exception):

  pass
 
class OCRError(DocumentProcessingError):

  pass
 
class ExtractionError(DocumentProcessingError):

  pass
 
class ValidationError(DocumentProcessingError):

  pass

```
 
**Retry Strategy**:

- Transient errors: Exponential backoff (1s, 2s, 4s)

- Permanent errors: Log and move to dead-letter queue

- Max retries: 3 attempts per document
 
### 5. Performance Optimization
 
**Caching**:

```python

@cache(ttl=86400)  # 24 hours

def get_loinc_code(code):

  return loinc_db.lookup(code)
 
@cache(ttl=3600)   # 1 hour

def get_normal_ranges(test_type):

  return ranges_db.get_ranges(test_type)

```
 
**Batch Processing**:

- Queue documents in batches

- Process 100 documents in parallel

- Throughput: 6000 docs/hour on single instance
 
### 6. Monitoring & Metrics
 
**Key Metrics**:

```python

# Extraction accuracy

accuracy_rate = (correct_extractions / total_extractions) * 100
 
# Processing performance

avg_processing_time = sum(processing_times) / len(processing_times)

p95_latency = percentile(processing_times, 0.95)
 
# Error rates

ocr_error_rate = (ocr_errors / total_documents) * 100

validation_error_rate = (validation_errors / total_extractions) * 100

```
 
**Prometheus Metrics**:

```

documents_processed_total{status="completed"}

documents_processing_duration_ms

extraction_confidence_score

validation_errors_total

```
 
### 7. Security Implementation
 
**Encryption**:

- PII fields encrypted at rest with AES-256

- TLS 1.3 for all API communications

- HSM for key management

- Key rotation every 90 days
 
**Access Control**:

- JWT with 1-hour expiration

- RBAC: Admin, Clinician, Analyst

- API rate limiting: 1000 req/min per user

- Audit logging of all extractions

 