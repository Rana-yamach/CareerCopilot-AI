import { apiClient } from './client';
import { mockGetProfile, mockLogin, mockRegister } from './mockAuth';
import { config } from '@/config';
import { useAuthStore } from '@/store/authStore';
import type {
  AuthResponse,
  LoginRequest,
  RefreshRequest,
  RefreshResponse,
  RegisterRequest,
  UpdateProfileRequest,
  UserProfile,
} from '@/types/auth';

export async function register(payload: RegisterRequest): Promise<AuthResponse> {
  if (config.useMockAuth) return mockRegister(payload.email, payload.password);
  const { data } = await apiClient.post<AuthResponse>('/auth/register', payload);
  return data;
}

export async function login(payload: LoginRequest): Promise<AuthResponse> {
  if (config.useMockAuth) return mockLogin(payload.email, payload.password);
  const { data } = await apiClient.post<AuthResponse>('/auth/login', payload);
  return data;
}

export async function refreshToken(payload: RefreshRequest): Promise<RefreshResponse> {
  const { data } = await apiClient.post<RefreshResponse>('/auth/refresh', payload);
  return data;
}

export async function getProfile(): Promise<UserProfile> {
  if (config.useMockAuth) {
    const userId = useAuthStore.getState().user?.user_id;
    if (!userId) throw new Error('Not authenticated');
    return mockGetProfile(userId);
  }
  const { data } = await apiClient.get<UserProfile>('/profile');
  return data;
}

export async function updateProfile(payload: UpdateProfileRequest): Promise<UserProfile> {
  const { data } = await apiClient.patch<UserProfile>('/profile', payload);
  return data;
}
