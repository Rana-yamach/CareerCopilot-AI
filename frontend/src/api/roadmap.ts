import { apiClient } from './client';
import type {
  ActiveRoadmapResponse,
  GenerateRoadmapRequest,
  GenerateRoadmapResponse,
  Roadmap,
  UpdateRoadmapTaskRequest,
  UpdateRoadmapTaskResponse,
} from '@/types/roadmap';

export async function generateRoadmap(
  payload: GenerateRoadmapRequest,
): Promise<GenerateRoadmapResponse> {
  const { data } = await apiClient.post<GenerateRoadmapResponse>('/roadmap/generate', payload);
  return data;
}

export async function getRoadmap(roadmapId: string): Promise<Roadmap> {
  const { data } = await apiClient.get<Roadmap>(`/roadmap/${roadmapId}`);
  return data;
}

export async function getActiveRoadmap(): Promise<ActiveRoadmapResponse> {
  const { data } = await apiClient.get<ActiveRoadmapResponse>('/roadmap/active');
  return data;
}

export async function updateRoadmapTask(
  roadmapId: string,
  taskId: string,
  payload: UpdateRoadmapTaskRequest,
): Promise<UpdateRoadmapTaskResponse> {
  const { data } = await apiClient.patch<UpdateRoadmapTaskResponse>(
    `/roadmap/${roadmapId}/task/${taskId}`,
    payload,
  );
  return data;
}
