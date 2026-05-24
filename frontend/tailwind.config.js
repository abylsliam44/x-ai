/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:        '#000000',
        surface:   '#0a0a0a',
        surface2:  '#111111',
        border:    '#1f1f1f',
        border2:   '#2a2a2a',
        tx:        '#ffffff',
        tx2:       '#a8a8a8',
        tx3:       '#6e6e6e',
        tx4:       '#404040',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'system-ui', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'Menlo', 'monospace'],
      },
      borderRadius: {
        pill: '999px',
      },
    },
  },
  plugins: [],
}
