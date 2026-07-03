/** API_CONTRACT.md §3 Documents */

export type DocumentType = 'cv' | 'linkedin_pdf' | 'generated_cv';

export type DocumentStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface ParsedSkills {
  languages: string[];
  frameworks: string[];
  tools: string[];
  experience: unknown[];
  education: unknown[];
}

export interface UploadDocumentResponse {
  task_id: string;
  document_id: string;
  document_type: DocumentType;
  status: DocumentStatus;
}

export interface DocumentStatusResponse {
  document_id: string;
  document_type: DocumentType;
  status: DocumentStatus;
  error_message: string | null;
}

export interface DocumentSummary {
  document_id: string;
  document_type: DocumentType;
  cv_score: number | null;
  cv_score_explanation: string | null;
  parsed_skills: ParsedSkills;
  status: DocumentStatus;
  uploaded_at: string;
}

export interface LatestDocumentsResponse {
  documents: DocumentSummary[];
}

export interface DocumentListResponse {
  items: DocumentSummary[];
  total: number;
}
