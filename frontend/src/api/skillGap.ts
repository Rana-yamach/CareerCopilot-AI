import { apiClient } from './client';
import type {
  AnalyzeSkillGapRequest,
  AnalyzeSkillGapResponse,
  LatestSkillGapResponse,
  SkillGapReport,
} from '@/types/skillGap';

export async function analyzeSkillGap(
  payload: AnalyzeSkillGapRequest,
): Promise<AnalyzeSkillGapResponse> {
  const { data } = await apiClient.post<AnalyzeSkillGapResponse>('/skill-gap/analyze', payload);
  return data;
}

export async function getSkillGapReport(reportId: string): Promise<SkillGapReport> {
  const { data } = await apiClient.get<SkillGapReport>(`/skill-gap/${reportId}`);
  return data;
}

export async function getLatestSkillGap(): Promise<LatestSkillGapResponse> {
  const { data } = await apiClient.get<LatestSkillGapResponse>('/skill-gap/latest');
  return data;
}
