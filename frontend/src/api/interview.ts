import { apiClient } from './client';
import type {
  AnswerInterviewRequest,
  AnswerInterviewResponse,
  InterviewSessionsResponse,
  InterviewSummary,
  StartInterviewRequest,
  StartInterviewResponse,
} from '@/types/interview';

export async function startInterview(
  payload: StartInterviewRequest,
): Promise<StartInterviewResponse> {
  const { data } = await apiClient.post<StartInterviewResponse>('/interview/start', payload);
  return data;
}

export async function submitAnswer(
  sessionId: string,
  payload: AnswerInterviewRequest,
): Promise<AnswerInterviewResponse> {
  const { data } = await apiClient.post<AnswerInterviewResponse>(
    `/interview/${sessionId}/answer`,
    payload,
  );
  return data;
}

export async function getInterviewSummary(sessionId: string): Promise<InterviewSummary> {
  const { data } = await apiClient.get<InterviewSummary>(`/interview/${sessionId}/summary`);
  return data;
}

export async function listInterviewSessions(params?: {
  limit?: number;
  offset?: number;
}): Promise<InterviewSessionsResponse> {
  const { data } = await apiClient.get<InterviewSessionsResponse>('/interview/sessions', {
    params,
  });
  return data;
}
