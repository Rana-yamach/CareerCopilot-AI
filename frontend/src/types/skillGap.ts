/** API_CONTRACT.md §5 Analysis — Skill Gap */

export type TaskStatus = 'queued' | 'processing' | 'completed' | 'failed';

export interface AnalyzeSkillGapRequest {
  target_position: string;
}

export interface AnalyzeSkillGapResponse {
  task_id: string;
  report_id: string;
  status: 'queued';
}

export interface SkillResource {
  title: string;
  type: string;
  url: string;
}

export interface MissingSkill {
  name: string;
  priority: number;
  estimated_weeks: number;
  resources: SkillResource[];
}

export interface SkillGapReport {
  report_id: string;
  user_id: string;
  target_position: string;
  match_score: number;
  source_document_ids: string[];
  missing_skills: MissingSkill[];
  status: TaskStatus;
  generated_at: string;
}

export interface LatestSkillGapResponse {
  report?: SkillGapReport | null;
}
