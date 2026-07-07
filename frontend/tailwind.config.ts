import type { Config } from 'tailwindcss';

const config: Config = {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // Marka rengi: tek-tonlu mavi skala (Primary #1A56DB = primary-700).
        // İsim alanı (primary-*) korunmuştur; proje genelinde onlarca dosyada
        // `primary-500/600/700` vb. kullanılıyor, yalnızca HEX değerleri
        // güncellenmiştir.
        primary: {
          50: '#ebf5ff',
          100: '#e1effe',
          200: '#c3ddfd',
          300: '#a4cafe',
          400: '#76a9fa',
          500: '#3f83f8',
          600: '#1c64f2',
          700: '#1a56db',
          800: '#1e429f',
          900: '#233876',
        },
        // Vurgu rengi: sıcak amber/turuncu. CV skorları, ilerleme yüzdeleri,
        // rozetler gibi "öne çıkan" sayısal/durum göstergeleri için kullanılır —
        // soğuk marka rengine karşı sıcak bir kontrast yaratır.
        accent: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },
        // Semantic tema token'ları — globals.css'teki CSS değişkenlerine bağlıdır
        // ve `.dark` sınıfı <html>'e eklendiğinde otomatik olarak değer değiştirir.
        // Kullanım: bg-app, bg-surface, bg-surface-2, border-border, text-default,
        // text-muted, text-faint (bkz. globals.css üstündeki eşleştirme tablosu).
        app: 'rgb(var(--color-bg) / <alpha-value>)',
        surface: 'rgb(var(--color-surface) / <alpha-value>)',
        'surface-2': 'rgb(var(--color-surface-2) / <alpha-value>)',
        border: 'rgb(var(--color-border) / <alpha-value>)',
        default: 'rgb(var(--color-text) / <alpha-value>)',
        muted: 'rgb(var(--color-text-muted) / <alpha-value>)',
        faint: 'rgb(var(--color-text-faint) / <alpha-value>)',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
};

export default config;
