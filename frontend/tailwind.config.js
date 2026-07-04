/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        ink: {
          950: '#08080B',
          900: '#0E0E13',
          800: '#15151C',
          700: '#1E1E27',
          600: '#2A2A35',
          500: '#3D3D4A',
        },
        signal: {
          DEFAULT: '#E8912E',
          soft: '#F2B366',
          dim: '#8A5A24',
        },
        mist: {
          100: '#F4F4F6',
          300: '#B8B8C4',
          500: '#7C7C8C',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        sans: ['"Inter"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      boxShadow: {
        glow: '0 0 0 1px rgba(232,145,46,0.25), 0 8px 40px -8px rgba(232,145,46,0.25)',
      },
      keyframes: {
        pulse-dot: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.35 },
        },
        rise: {
          '0%': { opacity: 0, transform: 'translateY(8px)' },
          '100%': { opacity: 1, transform: 'translateY(0)' },
        },
      },
      animation: {
        'pulse-dot': 'pulse-dot 1.6s ease-in-out infinite',
        rise: 'rise 0.4s ease-out both',
      },
    },
  },
  plugins: [],
}
