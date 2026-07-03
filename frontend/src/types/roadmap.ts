/** API_CONTRACT.md §6 Analysis — Roadmap */

import type { TaskStatus } from './skillGap';

export interface GenerateRoadmapRequest {
  skill_gap_report_id: string;
  weekly_hours: number;
}

export interface GenerateRoadmapResponse {
  task_id: string;
  roadmap_id: string;
  status: 'queued';
}

export interface RoadmapMilestone {
  week: number;
  title: string;
}

export interface RoadmapTask {
  task_id: string;
  title: string;
  done: boolean;
  resource: string;
}

export interface RoadmapWeekPlan {
  week: number;
  theme: string;
  tasks: RoadmapTask[];
}

export interface Roadmap {
  roadmap_id: string;
  user_id: string;
  skill_gap_report_id: string;
  weeks_total: number;
  weekly_hours: number;
  milestones: RoadmapMilestone[];
  plan: RoadmapWeekPlan[];
  progress_percent: number;
  status: TaskStatus;
  created_at: string;
}

export interface ActiveRoadmapResponse {
  roadmap?: Roadmap | null;
}

export interface UpdateRoadmapTaskRequest {
  done: boolean;
}

export interface UpdateRoadmapTaskResponse {
  task_id: string;
  done: boolean;
  progress_percent: number;
}
