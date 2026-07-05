import { apiClient } from './client';
import type {
  ConnectGithubRequest,
  ConnectGithubResponse,
  GithubProjectsResponse,
  GithubSyncResponse,
} from '@/types/github';

export async function connectGithub(
  payload: ConnectGithubRequest,
): Promise<ConnectGithubResponse> {
  const { data } = await apiClient.post<ConnectGithubResponse>('/github/connect', payload);
  return data;
}

export async function syncGithub(): Promise<GithubSyncResponse> {
  const { data } = await apiClient.get<GithubSyncResponse>('/github/sync');
  return data;
}

export async function getGithubProjects(): Promise<GithubProjectsResponse> {
  const { data } = await apiClient.get<GithubProjectsResponse>('/github/projects');
  return data;
}
