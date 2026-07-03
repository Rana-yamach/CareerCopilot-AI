import type { AuthResponse, UserProfile } from '@/types/auth';
import { tr } from '@/i18n/tr';
import { MockAuthError } from './client';

/**
 * Backend hazır olana kadar sadece bu tarayıcıda çalışan sahte kimlik
 * doğrulama. `config.useMockAuth` true iken `api/auth.ts` bu modülü kullanır.
 * Hiçbir ağ isteği yapılmaz; kullanıcı(lar) localStorage'da saklanır.
 * Backend gelince `VITE_USE_MOCK_AUTH` kapatılır, bu dosyaya dokunulmaz.
 */

const STORAGE_KEY = 'careercopilot-mock-users';

interface StoredMockUser {
  user_id: string;
  email: string;
  password: string;
  created_at: string;
}

function loadUsers(): StoredMockUser[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as StoredMockUser[]) : [];
  } catch {
    return [];
  }
}

function saveUsers(users: StoredMockUser[]): void {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(users));
}

function issueTokens(userId: string) {
  const stamp = Date.now();
  return {
    access_token: `mock.${userId}.${stamp}`,
    refresh_token: `mock-refresh.${userId}.${stamp}`,
    token_type: 'bearer' as const,
    expires_in: 3600,
  };
}

function simulateLatency(): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, 250));
}

export async function mockRegister(email: string, password: string): Promise<AuthResponse> {
  await simulateLatency();
  const users = loadUsers();
  if (users.some((u) => u.email.toLowerCase() === email.toLowerCase())) {
    throw new MockAuthError('CONFLICT', tr.auth.emailConflict);
  }
  const user: StoredMockUser = {
    user_id: crypto.randomUUID(),
    email,
    password,
    created_at: new Date().toISOString(),
  };
  users.push(user);
  saveUsers(users);
  return { user_id: user.user_id, email: user.email, ...issueTokens(user.user_id) };
}

export async function mockLogin(email: string, password: string): Promise<AuthResponse> {
  await simulateLatency();
  const user = loadUsers().find(
    (u) => u.email.toLowerCase() === email.toLowerCase() && u.password === password,
  );
  if (!user) {
    throw new MockAuthError('UNAUTHORIZED', tr.auth.invalidCredentials);
  }
  return { user_id: user.user_id, email: user.email, ...issueTokens(user.user_id) };
}

export async function mockGetProfile(userId: string): Promise<UserProfile> {
  await simulateLatency();
  const user = loadUsers().find((u) => u.user_id === userId);
  if (!user) {
    throw new MockAuthError('UNAUTHORIZED', tr.auth.sessionExpired);
  }
  return {
    user_id: user.user_id,
    email: user.email,
    github_username: null,
    target_position: null,
    target_company: null,
    created_at: user.created_at,
    updated_at: user.created_at,
  };
}
