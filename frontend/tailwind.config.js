/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Poppins', 'system-ui', 'sans-serif'],
        pixel: ['"Press Start 2P"', 'monospace'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        cyber: {
          bg: '#0b0f19',
          card: '#131b2e',
          cardHover: '#18223a',
          surface: '#1c2842',
          border: '#2a3b5e',
          borderGlow: '#3b82f6',
          purple: '#7c3aed',
          cyan: '#00f0ff',
          neonCyan: '#06b6d4',
          orange: '#ff5722',
          coral: '#f97316',
        }
      }
    },
  },
  plugins: [],
}
