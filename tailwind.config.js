/**
 * @fileoverview Tailwind CSS configuration for TRAIDER V1
 * @module tailwind.config.js
 * 
 * @description
 * Institutional-grade design system configuration for autonomous trading platform.
 * Includes custom color palette, trading-specific components, and responsive
 * breakpoints optimized for financial dashboards.
 * 
 * @design
 * - Professional trading color scheme
 * - Responsive grid system for dashboards
 * - Custom components for financial data display
 * 
 * @performance
 * - Purge unused styles in production
 * - Optimized for bundle size
 * 
 * @see {@link https://tailwindcss.com/docs/configuration}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

/* eslint-disable @typescript-eslint/no-require-imports */

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  
  theme: {
    extend: {
      // TRAIDER Brand Colors - Institutional Trading Theme
      colors: {
        // Base system colors
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
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        
        // Secondary colors
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        
        // Destructive colors
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        
        // Muted colors
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        
        // Accent colors
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        
        // Popover colors
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        
        // Card colors
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },

        // Trading Status Colors
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e', // Profit green
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },

        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444', // Loss red
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d',
        },

        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b', // Alert amber
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },

        // Neutral Colors for Professional UI
        neutral: {
          50: '#fafafa',
          100: '#f5f5f5',
          200: '#e5e5e5',
          300: '#d4d4d4',
          400: '#a3a3a3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },

        // Dark Theme Colors
        dark: {
          bg: '#0f172a',      // Background
          surface: '#1e293b', // Cards/surfaces
          border: '#334155',  // Borders
          text: '#f1f5f9',    // Primary text
          muted: '#94a3b8',   // Secondary text
        },

        // Trading-Specific Colors
        trading: {
          long: '#22c55e',    // Long position
          short: '#ef4444',   // Short position
          neutral: '#6b7280', // No position
          volume: '#8b5cf6',  // Volume bars
          spread: '#f59e0b',  // Bid-ask spread
        },
      },

      // Typography for Financial Data
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'Consolas', 'monospace'],
        display: ['Poppins', 'system-ui', 'sans-serif'],
      },

      // Spacing for Dashboard Layouts
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '112': '28rem',
        '128': '32rem',
      },

      // Screen Breakpoints for Trading Dashboards
      screens: {
        'xs': '475px',
        '3xl': '1600px',
        '4xl': '2000px',
      },

      // Animation for Live Data Updates
      animation: {
        'pulse-success': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'pulse-danger': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-subtle': 'bounce 1s ease-in-out 2',
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'flash-profit': 'flashProfit 0.5s ease-in-out',
        'flash-loss': 'flashLoss 0.5s ease-in-out',
      },

      // Custom Keyframes
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        flashProfit: {
          '0%, 100%': { backgroundColor: 'transparent' },
          '50%': { backgroundColor: 'rgb(34 197 94 / 0.2)' },
        },
        flashLoss: {
          '0%, 100%': { backgroundColor: 'transparent' },
          '50%': { backgroundColor: 'rgb(239 68 68 / 0.2)' },
        },
      },

      // Box Shadow for Cards and Modals
      boxShadow: {
        'card': '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
        'card-hover': '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
        'modal': '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
        'glow-success': '0 0 20px rgb(34 197 94 / 0.3)',
        'glow-danger': '0 0 20px rgb(239 68 68 / 0.3)',
      },

      // Border Radius for Consistent Design
      borderRadius: {
        'card': '0.75rem',
        'button': '0.5rem',
      },

      // Grid Template for Dashboard Layouts
      gridTemplateColumns: {
        'dashboard': 'minmax(250px, 1fr) 4fr',
        'cards': 'repeat(auto-fit, minmax(300px, 1fr))',
        'metrics': 'repeat(auto-fit, minmax(200px, 1fr))',
      },

      // Z-Index Scale
      zIndex: {
        'dropdown': '1000',
        'modal': '1050',
        'toast': '1100',
      },
    },
  },

  // Plugins for Enhanced Functionality
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio'),
    
    // Custom Plugin for Trading Components
    function({ addComponents, theme }) {
      addComponents({
        // Trading Card Component
        '.trading-card': {
          backgroundColor: theme('colors.white'),
          borderRadius: theme('borderRadius.card'),
          boxShadow: theme('boxShadow.card'),
          padding: theme('spacing.6'),
          border: `1px solid ${theme('colors.neutral.200')}`,
          transition: 'all 0.2s ease-in-out',
          '&:hover': {
            boxShadow: theme('boxShadow.card-hover'),
          },
        },

        // Metric Display Component
        '.metric-display': {
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          padding: theme('spacing.4'),
          backgroundColor: theme('colors.neutral.50'),
          borderRadius: theme('borderRadius.lg'),
          border: `1px solid ${theme('colors.neutral.200')}`,
        },

        // Status Indicator Component
        '.status-indicator': {
          display: 'inline-flex',
          alignItems: 'center',
          padding: `${theme('spacing.1')} ${theme('spacing.3')}`,
          borderRadius: theme('borderRadius.full'),
          fontSize: theme('fontSize.sm'),
          fontWeight: theme('fontWeight.medium'),
        },

        // Price Change Component
        '.price-change': {
          display: 'inline-flex',
          alignItems: 'center',
          fontFamily: theme('fontFamily.mono'),
          fontWeight: theme('fontWeight.semibold'),
          '&.positive': {
            color: theme('colors.success.600'),
          },
          '&.negative': {
            color: theme('colors.danger.600'),
          },
        },
      });
    },
  ],

  // Dark Mode Configuration
  darkMode: 'class',
}; 