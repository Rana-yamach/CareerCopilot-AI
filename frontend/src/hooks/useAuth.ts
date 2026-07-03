import { useQuery } from '@tanstack/react-query';
import { getProfile } from '@/api/auth';
import { useAuthStore } from '@/store/authStore';

/**
 * Mevcut kullanıcının profilini `GET /profile` üzerinden çeker.
 * Yalnızca kimliği doğrulanmış kullanıcılar için etkinleştirilir.
 */
export function useProfile() {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  return useQuery({
    queryKey: ['profile'],
    queryFn: getProfile,
    enabled: isAuthenticated,
    staleTime: 60_000,
  });
}

export function useAuth() {
  const user = useAuthStore((state) => state.user);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const logout = useAuthStore((state) => state.logout);

  return { user, isAuthenticated, logout };
}
