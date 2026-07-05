import { apiClient } from './client';
import type { ChatSessionMessagesResponse, ChatSessionsResponse } from '@/types/chat';

export async function getChatSessions(): Promise<ChatSessionsResponse> {
  const { data } = await apiClient.get<ChatSessionsResponse>('/agent/sessions');
  return data;
}

export async function getSessionMessages(
  sessionId: string,
  params?: { limit?: number; before?: string },
): Promise<ChatSessionMessagesResponse> {
  const { data } = await apiClient.get<ChatSessionMessagesResponse>(
    `/agent/sessions/${sessionId}/messages`,
    { params },
  );
  return data;
}
