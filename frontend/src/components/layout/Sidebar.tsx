import { NavLink } from 'react-router-dom';
import { tr } from '@/i18n/tr';

interface SidebarProps {
  open: boolean;
  onClose: () => void;
}

interface NavItem {
  to: string;
  label: string;
  icon: string;
}

const navItems: NavItem[] = [
  { to: '/dashboard', label: tr.nav.dashboard, icon: '\u{1F3E0}' },
  { to: '/documents', label: tr.nav.documents, icon: '\u{1F4C4}' },
  { to: '/cv/builder/sections', label: tr.nav.cvBuilder, icon: '\u{1F4DD}' },
  { to: '/skill-gap', label: tr.nav.skillGap, icon: '\u{1F3AF}' },
  { to: '/roadmap', label: tr.nav.roadmap, icon: '\u{1F5FA}\u{FE0F}' },
  { to: '/interview', label: tr.nav.interview, icon: '\u{1F399}\u{FE0F}' },
  { to: '/chat', label: tr.nav.chat, icon: '\u{1F4AC}' },
  { to: '/settings', label: tr.nav.settings, icon: '\u{2699}\u{FE0F}' },
];

function NavList({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="flex flex-1 flex-col gap-1 px-3 py-4" aria-label="Ana navigasyon">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors ${
              isActive
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
            }`
          }
        >
          <span aria-hidden="true">{item.icon}</span>
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

export function Sidebar({ open, onClose }: SidebarProps) {
  return (
    <>
      {/* Masaüstü sabit sidebar */}
      <aside className="hidden w-64 shrink-0 border-r border-gray-200 bg-white lg:flex lg:flex-col">
        <div className="flex h-16 items-center border-b border-gray-200 px-5">
          <span className="text-lg font-semibold text-primary-700">{tr.common.appName}</span>
        </div>
        <NavList />
      </aside>

      {/* Mobil drawer */}
      {open && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <button
            type="button"
            aria-label={tr.common.close}
            className="absolute inset-0 bg-black/40"
            onClick={onClose}
          />
          <aside className="relative flex h-full w-72 max-w-[80%] flex-col bg-white shadow-xl">
            <div className="flex h-16 items-center justify-between border-b border-gray-200 px-5">
              <span className="text-lg font-semibold text-primary-700">{tr.common.appName}</span>
              <button
                type="button"
                onClick={onClose}
                aria-label={tr.common.close}
                className="rounded-md p-1 text-gray-500 hover:bg-gray-100"
              >
                ✕
              </button>
            </div>
            <NavList onNavigate={onClose} />
          </aside>
        </div>
      )}
    </>
  );
}
