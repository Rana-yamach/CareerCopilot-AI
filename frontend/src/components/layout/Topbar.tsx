import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { useAuthStore } from '@/store/authStore';
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
    <header className="flex h-16 items-center justify-between border-b border-gray-200 bg-white px-4 sm:px-6">
      <button
        type="button"
        onClick={onMenuClick}
        className="rounded-md p-2 text-gray-600 hover:bg-gray-100 lg:hidden"
        aria-label="Menüyü aç"
      >
        <span aria-hidden="true">☰</span>
      </button>

      <div className="hidden lg:block" />

      <div className="flex items-center gap-4">
        <span className="text-sm font-medium text-gray-700">{user?.email}</span>
        <button
          type="button"
          onClick={handleLogout}
          className="btn-secondary !px-3 !py-1.5 text-sm"
        >
          {tr.common.logout}
        </button>
      </div>
    </header>
  );
}
