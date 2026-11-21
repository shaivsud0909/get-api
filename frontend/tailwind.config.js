/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f2f7f3',
          100: '#e0ebe2',
          200: '#c2d7c7',
          300: '#99bca2',
          400: '#6c9c79',
          500: '#4c7f5b',
          600: '#396547',
          700: '#2e513a',
          800: '#274230',
          900: '#213729',
          950: '#111e16',
        },
        cream: {
          50: '#fdfcf9',
          100: '#faf7f0',
          200: '#f3ede0',
          300: '#eae0cb',
        },
        clay: {
          100: '#f0e6dc',
          200: '#e0cdba',
          300: '#cbab8d',
          400: '#b58a64',
          500: '#a2744f',
          600: '#8a5f42',
          700: '#704c38',
          800: '#5d4032',
          900: '#4e372c',
        },
      },
      fontFamily: {
        display: ['Fraunces', 'Georgia', 'serif'],
        body: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
      },
      keyframes: {
        'fade-up': {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
      },
      animation: {
        'fade-up': 'fade-up 0.6s ease-out both',
        'fade-in': 'fade-in 0.4s ease-out both',
      },
    },
  },
  plugins: [],
};
