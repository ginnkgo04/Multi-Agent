/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        pink: {
          50: '#fdf2f8',
          100: '#fce7f3',
          200: '#fbcfe8',
          300: '#f9a8d4',
          400: '#f472b6',
          500: '#ec4899',
          600: '#db2777',
          700: '#be185d',
          800: '#9d174d',
          900: '#831843',
          950: '#500724',
        },
        rose: {
          50: '#fff1f2',
          100: '#ffe4e6',
          200: '#fecdd3',
          300: '#fda4af',
          400: '#fb7185',
          500: '#f43f5e',
          600: '#e11d48',
          700: '#be123c',
          800: '#9f1239',
          900: '#881337',
          950: '#4c0519',
        },
        pig: {
          light: '#ffd6e7',
          DEFAULT: '#ffb6c1',
          dark: '#ff8fa3',
          nose: '#ff6b8b',
          ear: '#ff477e',
        }
      },
      fontFamily: {
        'cute': ['"Comic Sans MS"', '"Comic Sans"', 'cursive'],
        'playful': ['"Nunito"', 'sans-serif'],
      },
      animation: {
        'float': 'float 3s ease-in-out infinite',
        'wiggle': 'wiggle 1s ease-in-out infinite',
        'bounce-slow': 'bounce 2s infinite',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pig-nose': 'pig-nose 2s ease-in-out infinite',
        'heart-beat': 'heart-beat 1.5s ease-in-out infinite',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        'pig-nose': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
        },
        'heart-beat': {
          '0%, 100%': { transform: 'scale(1)' },
          '50%': { transform: 'scale(1.1)' },
        },
      },
      backgroundImage: {
        'gradient-pig': 'linear-gradient(135deg, #f472b6 0%, #fb7185 100%)',
        'gradient-pig-light': 'linear-gradient(135deg, #fce7f3 0%, #ffe4e6 100%)',
        'gradient-pig-dark': 'linear-gradient(135deg, #db2777 0%, #be123c 100%)',
        'pig-pattern': "url(\"data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23f472b6' fill-opacity='0.1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E\")",
      },
      borderRadius: {
        '4xl': '2rem',
        '5xl': '2.5rem',
        '6xl': '3rem',
      },
      boxShadow: {
        'pig': '0 10px 25px -5px rgba(244, 114, 182, 0.3)',
        'pig-lg': '0 20px 40px -10px rgba(244, 114, 182, 0.4)',
        'pig-xl': '0 25px 50px -12px rgba(244, 114, 182, 0.5)',
        'pig-inner': 'inset 0 2px 4px 0 rgba(244, 114, 182, 0.1)',
      },
    },
  },
  plugins: [],
}