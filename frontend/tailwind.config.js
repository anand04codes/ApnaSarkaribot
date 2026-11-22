/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        sarkari: {
          blue: '#1E3A8A',
          saffron: '#FF671F',
          green: '#046A38',
          danger: '#DC2626',
          warning: '#D97706',
          success: '#16A34A',
          surface: '#F8FAFC',
          darkBg: '#0F172A',
          darkCard: '#1E293B'
        }
      },
      fontFamily: {
        sans: ['Inter', 'Noto Sans Devanagari', 'system-ui', 'sans-serif'],
      }
    },
  },
  plugins: [],
}

