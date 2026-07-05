/** API_CONTRACT.md §9 Agent — Chat / Orchestrator */

export type ChatRole = 'user' | 'assistant';

export type AgentIntent = 'cv_agent' | 'skill_gap' | 'roadmap' | 'interview' | 'cv_writer' | 'general';

export interface SendChatMessageRequest {
  message: string;
  session_id: string | null;
}

export interface ChatMetadataEvent {
  session_id: string;
  message_id: string;
  intent: AgentIntent;
  agent: string;
}

export interface ChatTokenEvent {
  token: string;
}

export interface ChatErrorEvent {
  code: string;
  message: string;
}

export interface ChatSessionSummary {
  session_id: string;
  last_message_preview: string;
  last_agent: string;
  message_count: number;
  started_at: string;
  last_message_at: string;
}

export interface ChatSessionsResponse {
  sessions: ChatSessionSummary[];
}

export interface ChatMessage {
  message_id: string;
  role: ChatRole;
  content: string;
  agent_used?: string;
  created_at: string;
}

export interface ChatSessionMessagesResponse {
  session_id: string;
  messages: ChatMessage[];
}
