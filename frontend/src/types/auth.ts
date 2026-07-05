/** API_CONTRACT.md §1 Auth */

export interface RegisterRequest {
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user_id: string;
  email: string;
  access_token: string;
  refresh_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface RefreshRequest {
  refresh_token: string;
}

export interface RefreshResponse {
  access_token: string;
  token_type: 'bearer';
  expires_in: number;
}

export interface UserProfile {
  user_id: string;
  email: string;
  github_username: string | null;
  target_position: string | null;
  target_company: string | null;
  created_at: string;
  updated_at: string;
}

export interface UpdateProfileRequest {
  github_username?: string;
  target_position?: string;
  target_company?: string;
}
