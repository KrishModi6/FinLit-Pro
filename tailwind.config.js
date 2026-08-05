/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  // Dark mode is toggled by putting `class="dark"` on <html> (see ThemeContext).
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Site chrome. A navy/ink scale so the light theme reads like a textbook
        // and the dark theme reads like a trading terminal.
        ink: {
          50: '#f6f7f9',
          100: '#eceef2',
          200: '#d5dae3',
          300: '#b0b9c9',
          400: '#8492a9',
          500: '#64748b',
          600: '#4c5a70',
          700: '#3d485c',
          800: '#232c3d',
          900: '#151c2a',
          950: '#0b111c',
        },
        // Market semantics: green = up, red = down. Used sparingly and never as
        // the only signal (icons + labels carry the meaning too).
        up: '#10b981',
        down: '#ef4444',
      },
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui', '-apple-system', 'Segoe UI', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
      },
      maxWidth: {
        prose: '46rem',
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(6px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
      },
      animation: {
        'fade-up': 'fade-up .35s ease-out both',
      },
    },
  },
  plugins: [],
}
