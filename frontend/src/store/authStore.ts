import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { AuthResponse } from '@/types/auth';

interface AuthUser {
  user_id: string;
  email: string;
}

interface AuthState {
  user: AuthUser | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  setAuth: (auth: AuthResponse) => void;
  setAccessToken: (accessToken: string) => void;
  logout: () => void;
}

/**
 * Kimlik doğrulama durumu. `persist` middleware ile localStorage'a yazılır,
 * böylece sayfa yenilendiğinde oturum korunur (bkz. ARCHITECTURE.md §6.1).
 */
export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,

      setAuth: (auth) =>
        set({
          user: { user_id: auth.user_id, email: auth.email },
          accessToken: auth.access_token,
          refreshToken: auth.refresh_token,
          isAuthenticated: true,
        }),

      setAccessToken: (accessToken) => set({ accessToken }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        }),
    }),
    {
      name: 'careercopilot-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    },
  ),
);
