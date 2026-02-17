/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        canvas: '#F7F6F3',
        surface: '#FFFFFF',
        rim: '#E8E3F0',
        ink: '#1E1B2E',
        muted: '#6B6680',
        purple: {
          DEFAULT: '#7B5EA7',
          dark:    '#5B3F87',
          light:   '#B39DCC',
          subtle:  '#F0EBF8',
        },
        sky: {
          DEFAULT: '#72B8D8',
          dark:    '#4A96BA',
          light:   '#BDE0F0',
          subtle:  '#EAF5FB',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
