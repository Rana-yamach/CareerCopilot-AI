import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  FileEdit,
  Target,
  Map,
  Mic,
  MessageCircle,
  Settings,
  X,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { tr } from '@/i18n/tr';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: tr.nav.dashboard, icon: LayoutDashboard },
  { to: '/documents', label: tr.nav.documents, icon: FileText },
  { to: '/cv/builder/sections', label: tr.nav.cvBuilder, icon: FileEdit },
  { to: '/skill-gap', label: tr.nav.skillGap, icon: Target },
  { to: '/roadmap', label: tr.nav.roadmap, icon: Map },
  { to: '/interview', label: tr.nav.interview, icon: Mic },
  { to: '/chat', label: tr.nav.chat, icon: MessageCircle },
  { to: '/settings', label: tr.nav.settings, icon: Settings },
];

function NavList({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-1 flex-col gap-1 px-3 py-4" aria-label="Ana navigasyon">
      {navItems.map((item) => {
        const Icon = item.icon;
        return (
          <NavLink
            key={item.to}
            to={item.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `group relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-primary-600/90 text-white shadow-lg shadow-primary-900/40'
                  : 'text-slate-300 hover:bg-white/5 hover:text-white'
              }`
            }
          >
            {({ isActive }) => (
              <>
                {isActive && (
                  <span
                    aria-hidden="true"
                    className="absolute -left-3 top-1/2 h-6 w-1 -translate-y-1/2 rounded-full bg-accent-400 shadow-[0_0_10px_2px_rgba(251,191,36,0.55)]"
                  />
                )}
                <Icon aria-hidden="true" className="h-5 w-5 shrink-0" />
                {item.label}
              </>
            )}
          </NavLink>
        );
      })}
    </nav>
  );
}

function BrandMark() {
  return (
    <div className="flex items-center gap-2.5">
      <span
        aria-hidden="true"
        className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-primary-700 text-xs font-bold text-white shadow-md shadow-primary-900/50"
      >
        CC
      </span>
      <span className="text-lg font-semibold text-white">{tr.common.appName}</span>
    </div>
  );
}

/**
 * Uygulamanın görsel çapası: koyu, camsı (glassmorphic) bir panel. Bilinçli
 * marka kararı olarak her iki temada da (açık/koyu) koyu kalır — bkz. tasarım
 * sistemi görevi.
 */
export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* Masaüstü sabit sidebar */}
      <aside className="hidden w-64 shrink-0 flex-col border-r border-white/5 bg-gradient-to-b from-slate-900 to-indigo-950 backdrop-blur-xl lg:flex">
        <div className="flex h-16 items-center border-b border-white/10 px-5">
          <BrandMark />
        </div>
        <NavList />
      </aside>

      {/* Mobil drawer */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label={tr.common.close}
            className="absolute inset-0 bg-black/50 backdrop-blur-sm"
            onClick={onClose}
          />
          <aside className="relative flex h-full w-72 max-w-[80%] flex-col bg-gradient-to-b from-slate-900 to-indigo-950 shadow-2xl">
            <div className="flex h-16 items-center justify-between border-b border-white/10 px-5">
              <BrandMark />
              <button
                type="button"
                onClick={onClose}
                aria-label={tr.common.close}
                className="rounded-md p-1 text-slate-300 hover:bg-white/10 hover:text-white"
              >
                <X aria-hidden="true" className="h-5 w-5" />
              </button>
            </div>
            <NavList onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
