import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Menu } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { ThemeToggle } from '@/components/ui/ThemeToggle';
import { tr } from '@/i18n/tr';

interface TopbarProps {
  onMenuClick: () => void;
}

export function Topbar({ onMenuClick }: TopbarProps) {
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    toast.success(tr.common.logoutSuccess);
    navigate('/login', { replace: true });
  }

  return (
    <header className="flex h-16 items-center justify-between border-b border-border bg-surface/80 px-4 backdrop-blur-md sm:px-6">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded-lg p-2 text-muted hover:bg-surface-2 hover:text-default lg:hidden"
        aria-label="Menüyü aç"
      >
        <Menu aria-hidden="true" className="h-5 w-5" />
      </button>

      <div className="hidden lg:block" />

      <div className="flex items-center gap-3 sm:gap-4">
        <ThemeToggle />
        <span className="max-w-[7rem] truncate text-sm font-medium text-muted sm:max-w-[12rem]">
          {user?.email}
        </span>
        <button type="button" onClick={handleLogout} className="btn-secondary !px-3 !py-1.5 text-sm">
          {tr.common.logout}
        </button>
      </div>
    </header>
  );
}
