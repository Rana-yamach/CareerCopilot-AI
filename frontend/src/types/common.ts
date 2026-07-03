/** API_CONTRACT.md — Ortak yanıt şemaları */

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
  };
}

export interface AsyncTaskAck {
  task_id: string;
  resource_id: string;
  status: 'queued';
}

export type ResourceType = 'document' | 'cv_draft' | 'skill_gap_report' | 'roadmap';

export interface TaskStatusResponse {
  task_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  resource_type: ResourceType;
  resource_id: string;
  progress_percent: number;
  error_code: string | null;
  error_message: string | null;
}
