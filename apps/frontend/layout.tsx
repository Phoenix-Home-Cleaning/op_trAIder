/**
 * @fileoverview Root layout for TRAIDER V1 application
 * @module app/layout
 *
 * @description
 * Root layout component that wraps all pages in the TRAIDER application.
 * Provides global styling, metadata, fonts, and authentication context.
 * Designed for institutional-grade trading platform requirements.
 *
 * @performance
 * - Latency target: N/A (static layout)
 * - Throughput: N/A
 * - Memory usage: <1MB
 *
 * @risk
 * - Failure impact: CRITICAL (affects entire application)
 * - Recovery strategy: Static fallback with error boundaries
 *
 * @compliance
 * - Audit requirements: No
 * - Data retention: N/A
 *
 * @see {@link docs/architecture/frontend.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import type { Metadata } from 'next';
import { Inter, JetBrains_Mono } from 'next/font/google';
import './globals.css';
import { Providers } from './providers';

/**
 * Inter font configuration for UI text
 *
 * @description Primary font for the application interface
 * @performance Preloaded for optimal rendering performance
 */
const inter = Inter({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
});

/**
 * JetBrains Mono font configuration for code and data display
 *
 * @description Monospace font for trading data, logs, and code
 * @performance Preloaded for trading dashboard performance
 */
const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-jetbrains-mono',
});

/**
 * Application metadata configuration
 *
 * @description SEO and social media metadata for TRAIDER platform
 * @compliance Meets institutional branding requirements
 */
export const metadata: Metadata = {
  title: {
    default: 'TRAIDER V1 - Institutional Crypto Trading Platform',
    template: '%s | TRAIDER V1',
  },
  description:
    'Autonomous cryptocurrency trading platform with institutional-grade risk management, real-time analytics, and machine learning-powered signals.',
  keywords: [
    'cryptocurrency trading',
    'institutional trading',
    'autonomous trading',
    'risk management',
    'machine learning',
    'algorithmic trading',
    'crypto portfolio management',
  ],
  authors: [{ name: 'TRAIDER Team' }],
  creator: 'TRAIDER Team',
  publisher: 'TRAIDER',
  robots: {
    index: false, // Private institutional platform
    follow: false,
    nocache: true,
    noarchive: true,
    noimageindex: true,
  },
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
  manifest: '/manifest.json',
  icons: {
    icon: '/favicon.ico',
    shortcut: '/favicon-16x16.png',
    apple: '/apple-touch-icon.png',
  },
};

/**
 * Root layout component
 *
 * @description
 * Provides the HTML structure and global context for all pages.
 * Includes font loading, CSS variables, and authentication providers.
 * Essential infrastructure component for the entire trading platform.
 *
 * @param {object} props - Component props
 * @param {React.ReactNode} props.children - Child components to render within the layout
 * @returns {JSX.Element} JSX element representing the root HTML structure
 *
 * @throws {Error} If providers fail to initialize
 *
 * @performance
 * - Font preloading for optimal rendering (<100ms)
 * - CSS variables for consistent theming
 * - Minimal DOM structure for performance
 * - Optimized hydration with suppressHydrationWarning
 *
 * @sideEffects
 * - Loads Google Fonts (Inter, JetBrains Mono)
 * - Sets up global CSS variables
 * - Initializes authentication providers
 * - Creates portal containers for modals
 *
 * @security
 * - Content Security Policy ready
 * - No external script injection
 * - Secure font loading with display=swap
 * - Mobile security headers configured
 *
 * @tradingImpact Foundation for entire trading platform interface
 * @riskLevel CRITICAL - Core application infrastructure
 *
 * @example
 * ```tsx
 * // Automatically wraps all pages in Next.js App Router
 * export default function Page() {
 *   return <div>Page content</div>;
 * }
 * ```
 *
 * @monitoring
 * - Metric: `layout.hydration_time`
 * - Alert threshold: > 500ms
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${inter.variable} ${jetbrainsMono.variable}`}
      suppressHydrationWarning
    >
      <head>
        <meta charSet="utf-8" />
        <meta name="format-detection" content="telephone=no" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="default" />
        <meta name="apple-mobile-web-app-title" content="TRAIDER V1" />
        <meta name="application-name" content="TRAIDER V1" />
        <meta name="msapplication-TileColor" content="#000000" />
        <meta name="msapplication-tap-highlight" content="no" />
      </head>
      <body className="min-h-screen bg-background font-sans antialiased">
        {/* Global loading indicator container */}
        <div id="loading-indicator" />

        {/* Main application content */}
        <main className="relative flex min-h-screen flex-col">
          <Providers>{children}</Providers>
        </main>

        {/* Portal container for modals and overlays */}
        <div id="modal-root" />

        {/* Development tools (only in development) */}
        {process.env.NODE_ENV === 'development' && <div id="dev-tools" />}
      </body>
    </html>
  );
}
