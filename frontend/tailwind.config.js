/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        surface: '#131313',
        'surface-dim': '#0a0a0a',
        'surface-bright': '#1f1f1f',
        'surface-container': '#1a1a1a',
        'surface-container-high': '#222222',
        'on-surface': '#e2e2e2',
        'on-surface-variant': '#666666',
        outline: '#444444',
        'outline-variant': '#222222',
        primary: '#ffffff',
        'on-primary': '#000000',
        secondary: '#c8c6c5',
        error: '#ef4444',
        success: '#22c55e',
        warning: '#f59e0b',
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'SF Mono', 'monospace'],
      },
      fontSize: {
        'display-lg': ['72px', { lineHeight: '1.1', letterSpacing: '-0.04em', fontWeight: '800' }],
        'headline-lg': ['40px', { lineHeight: '1.2', letterSpacing: '-0.02em', fontWeight: '700' }],
        'headline-md': ['24px', { lineHeight: '1.3', letterSpacing: '-0.01em', fontWeight: '600' }],
        'body-lg': ['18px', { lineHeight: '1.6', fontWeight: '400' }],
        'body-md': ['16px', { lineHeight: '1.6', fontWeight: '400' }],
        'label-md': ['14px', { lineHeight: '1.4', letterSpacing: '0.05em', fontWeight: '500' }],
        'label-sm': ['12px', { lineHeight: '1.4', letterSpacing: '0.1em', fontWeight: '500' }],
      },
      spacing: {
        'unit-1': '4px',
        'unit-2': '8px',
        'unit-4': '16px',
        'unit-6': '24px',
        'unit-8': '32px',
        'unit-12': '48px',
        'unit-16': '64px',
      },
      borderRadius: {
        DEFAULT: '0px',
        none: '0px',
      },
      borderWidth: {
        DEFAULT: '1px',
      },
    },
  },
  plugins: [],
};
