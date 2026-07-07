import { Moon, Sun } from 'lucide-react';
import { useThemeStore } from '@/store/themeStore';
import { tr } from '@/i18n/tr';

/**
 * Açık/koyu tema anahtarı. Güneş/ay ikonlu, animasyonlu pill switch.
 * `themeStore`'daki tercihe göre <html> öğesine `dark` sınıfı eklenir/kaldırılır
 * (bkz. globals.css CSS değişkenleri ve tailwind.config.ts semantic renkler).
 */
export function ThemeToggle() {
  const theme = useThemeStore((state) => state.theme);
  const toggleTheme = useThemeStore((state) => state.toggleTheme);
  const isDark = theme === 'dark';

  return (
    <button
      type="button"
      onClick={toggleTheme}
      role="switch"
      aria-checked={isDark}
      aria-label={isDark ? tr.common.switchToLightMode : tr.common.switchToDarkMode}
      title={isDark ? tr.common.switchToLightMode : tr.common.switchToDarkMode}
      className="relative inline-flex h-8 w-14 shrink-0 items-center rounded-full border border-border bg-surface-2 px-1 transition-colors duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 focus-visible:ring-offset-2 focus-visible:ring-offset-surface"
    >
      <span className="sr-only">{tr.common.toggleThemeSr}</span>
      <span
        aria-hidden="true"
        className={`flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-primary-500 to-primary-700 text-white shadow-sm transition-transform duration-200 ${
          isDark ? 'translate-x-6' : 'translate-x-0'
        }`}
      >
        {isDark ? (
          <Moon aria-hidden="true" className="h-3.5 w-3.5" />
        ) : (
          <Sun aria-hidden="true" className="h-3.5 w-3.5" />
        )}
      </span>
    </button>
  );
}
