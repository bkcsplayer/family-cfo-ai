/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'finance-black': '#111111',
        'finance-panel': '#1a1a1a',
        'neon-purple': '#bf5af2',
        'neon-purple-dim': '#bf5af220',
        'electric-green': '#28cd41', // A bit more readable than pure neon
        'signal-orange': '#ff9f0a',
        'muted-red': '#ff453a',
        'grid-border': '#ffffff10',
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      }
    },
  },
  plugins: [],
}
