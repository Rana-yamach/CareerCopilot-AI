import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type Theme = 'light' | 'dark';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
  toggleTheme: () => void;
}

function getInitialTheme(): Theme {
  return 'light';
}

function applyThemeClass(theme: Theme) {
  if (typeof document === 'undefined') return;
  document.documentElement.classList.toggle('dark', theme === 'dark');
}

/**
 * Açık/koyu tema durumu (bkz. tasarım sistemi görevi). `persist` middleware ile
 * localStorage'a `theme-storage` anahtarıyla yazılır, böylece sayfa
 * yenilendiğinde tercih korunur. Varsayılan tema — kullanıcı daha önce seçim
 * yapmadıysa — her zaman açık (light) temadır.
 *
 * "Flash of wrong theme" önlemi: `index.html` içinde React yüklenmeden önce
 * çalışan bir inline script, aynı localStorage anahtarını okuyarak <html>
 * öğesine senkron olarak `dark` sınıfını ekler. Bu store rehydrate olduğunda
 * (`onRehydrateStorage`) sınıfı tekrar doğrular.
 */
export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      theme: getInitialTheme(),

      setTheme: (theme) => {
        applyThemeClass(theme);
        set({ theme });
      },

      toggleTheme: () => {
        const next: Theme = get().theme === 'dark' ? 'light' : 'dark';
        applyThemeClass(next);
        set({ theme: next });
      },
    }),
    {
      name: 'theme-storage',
      onRehydrateStorage: () => (state) => {
        if (state) applyThemeClass(state.theme);
      },
    },
  ),
);
