/** API_CONTRACT.md §7 Interview */

export type InterviewDifficulty = 'junior' | 'mid';

export type InterviewCategory = 'algorithmic' | 'system' | 'behavioral';

export interface StartInterviewRequest {
  target_position: string;
  difficulty: InterviewDifficulty;
  category: InterviewCategory;
}

export interface StartInterviewResponse {
  session_id: string;
  question_index: number;
  question: string;
  target_position: string;
  difficulty: InterviewDifficulty;
  category: InterviewCategory;
  started_at: string;
}

export interface AnswerInterviewRequest {
  question_index: number;
  user_answer: string;
}

export interface AnsweredQuestion {
  question_index: number;
  question: string;
  user_answer: string;
  feedback: string;
  score: number;
  correct_answer_hint: string;
}

export interface NextQuestion {
  question_index: number;
  question: string;
}

export interface AnswerInterviewResponse {
  session_id: string;
  answered: AnsweredQuestion;
  next_question: NextQuestion | null;
  is_session_complete: boolean;
}

export interface InterviewSummary {
  session_id: string;
  target_position: string;
  difficulty: InterviewDifficulty;
  category: InterviewCategory;
  overall_score: number;
  questions: AnsweredQuestion[];
  strengths: string[];
  improvements: string[];
  started_at: string;
  ended_at: string;
}

export interface InterviewSessionListItem {
  session_id: string;
  target_position: string;
  category: InterviewCategory;
  overall_score: number;
  started_at: string;
  ended_at: string;
}

export interface InterviewSessionsResponse {
  items: InterviewSessionListItem[];
  total: number;
}
