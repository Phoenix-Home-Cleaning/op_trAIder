/**
 * @fileoverview Tailwind CSS 4 configuration for TRAIDER V1
 * @module tailwind.config.js
 * 
 * @description
 * Institutional-grade design system configuration for autonomous trading platform.
 * Updated for Tailwind CSS 4 with modern color system, trading-specific components, 
 * and responsive breakpoints optimized for financial dashboards.
 * 
 * @design
 * - Professional trading color scheme with CSS variables
 * - Responsive grid system for dashboards
 * - Custom components for financial data display
 * 
 * @performance
 * - Optimized for bundle size with CSS 4 features
 * - Native CSS cascade layers support
 * 
 * @see {@link https://tailwindcss.com/docs/configuration}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './**/*.{js,ts,jsx,tsx,mdx}',
    '../../packages/shared/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  
  theme: {
    extend: {
      // TRAIDER Brand Colors - Institutional Trading Theme
      colors: {
        // CSS Custom Properties for dynamic theming
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        
        // Primary Brand Colors
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          200: '#bae6fd',
          300: '#7dd3fc',
          400: '#38bdf8',
          500: '#0ea5e9', // Main brand color
          600: '#0284c7',
          700: '#0369a1',
          800: '#075985',
          900: '#0c4a6e',
          950: '#082f49',
          DEFAULT: 'hsl(var(--primary))',
          foreground: 'hsl(var(--primary-foreground))',
        },

        // Secondary Colors for UI Components
        secondary: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b',
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
          DEFAULT: 'hsl(var(--secondary))',
          foreground: 'hsl(var(--secondary-foreground))',
        },

        // Trading Status Colors
        trading: {
          // Profit/Loss indicators
          profit: {
            50: '#f0fdf4',
            100: '#dcfce7',
            200: '#bbf7d0',
            300: '#86efac',
            400: '#4ade80',
            500: '#22c55e', // Primary profit green
            600: '#16a34a',
            700: '#15803d',
            800: '#166534',
            900: '#14532d',
          },
          loss: {
            50: '#fef2f2',
            100: '#fee2e2',
            200: '#fecaca',
            300: '#fca5a5',
            400: '#f87171',
            500: '#ef4444', // Primary loss red
            600: '#dc2626',
            700: '#b91c1c',
            800: '#991b1b',
            900: '#7f1d1d',
          },
          
          // Market status
          bullish: '#22c55e',
          bearish: '#ef4444',
          neutral: '#6b7280',
          
          // Order types
          buy: '#10b981',
          sell: '#f59e0b',
          hold: '#6b7280',
        },

        // Alert and Status Colors
        destructive: {
          DEFAULT: 'hsl(var(--destructive))',
          foreground: 'hsl(var(--destructive-foreground))',
        },
        muted: {
          DEFAULT: 'hsl(var(--muted))',
          foreground: 'hsl(var(--muted-foreground))',
        },
        accent: {
          DEFAULT: 'hsl(var(--accent))',
          foreground: 'hsl(var(--accent-foreground))',
        },
        popover: {
          DEFAULT: 'hsl(var(--popover))',
          foreground: 'hsl(var(--popover-foreground))',
        },
        card: {
          DEFAULT: 'hsl(var(--card))',
          foreground: 'hsl(var(--card-foreground))',
        },

        // Dark theme variations
        dark: {
          background: '#0a0a0a',
          foreground: '#fafafa',
          card: '#161616',
          border: '#262626',
          primary: '#0ea5e9',
          secondary: '#525252',
        },
      },

      // Typography Scale for Financial Data
      fontSize: {
        'price-sm': ['0.75rem', { lineHeight: '1rem', fontWeight: '600' }],
        'price': ['0.875rem', { lineHeight: '1.25rem', fontWeight: '600' }],
        'price-lg': ['1rem', { lineHeight: '1.5rem', fontWeight: '600' }],
        'price-xl': ['1.125rem', { lineHeight: '1.75rem', fontWeight: '700' }],
        'display': ['2.25rem', { lineHeight: '2.5rem', fontWeight: '800' }],
      },

      // Spacing for Trading Components
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
        'sidebar': '16rem',
        'chart': '24rem',
      },

      // Animation for Real-time Updates
      animation: {
        'pulse-profit': 'pulse-profit 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-loss': 'pulse-loss 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'flash': 'flash 0.5s ease-in-out',
        'accordion-down': 'accordion-down 0.2s ease-out',
        'accordion-up': 'accordion-up 0.2s ease-out',
      },

      keyframes: {
        'pulse-profit': {
          '0%, 100%': { 
            opacity: '1',
            backgroundColor: 'rgb(34 197 94 / 0.1)'
          },
          '50%': { 
            opacity: '0.8',
            backgroundColor: 'rgb(34 197 94 / 0.3)'
          },
        },
        'pulse-loss': {
          '0%, 100%': { 
            opacity: '1',
            backgroundColor: 'rgb(239 68 68 / 0.1)'
          },
          '50%': { 
            opacity: '0.8',
            backgroundColor: 'rgb(239 68 68 / 0.3)'
          },
        },
        'slide-up': {
          'from': { transform: 'translateY(100%)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          'from': { transform: 'translateY(-100%)', opacity: '0' },
          'to': { transform: 'translateY(0)', opacity: '1' },
        },
        'flash': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.5' },
        },
        'accordion-down': {
          from: { height: '0' },
          to: { height: 'var(--radix-accordion-content-height)' },
        },
        'accordion-up': {
          from: { height: 'var(--radix-accordion-content-height)' },
          to: { height: '0' },
        },
      },

      // Box Shadow for Depth
      boxShadow: {
        'trading': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
        'trading-lg': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
        'glow': '0 0 20px rgba(14, 165, 233, 0.3)',
        'glow-profit': '0 0 20px rgba(34, 197, 94, 0.3)',
        'glow-loss': '0 0 20px rgba(239, 68, 68, 0.3)',
      },

      // Border Radius for Modern UI
      borderRadius: {
        lg: 'var(--radius)',
        md: 'calc(var(--radius) - 2px)',
        sm: 'calc(var(--radius) - 4px)',
      },

      // Grid Templates for Trading Layouts
      gridTemplateColumns: {
        'dashboard': '16rem 1fr 20rem',
        'trading': '1fr 24rem',
        'charts': 'repeat(auto-fit, minmax(300px, 1fr))',
      },

      // Responsive Breakpoints for Trading Displays
      screens: {
        'xs': '475px',
        'trading-sm': '640px',
        'trading-md': '768px', 
        'trading-lg': '1024px',
        'trading-xl': '1280px',
        'trading-2xl': '1536px',
        'ultra': '1920px',
      },
    },
  },

  // Tailwind CSS 4 doesn't need explicit plugins configuration
  // Built-in support for forms, typography, and aspect-ratio
  plugins: [],
}; 