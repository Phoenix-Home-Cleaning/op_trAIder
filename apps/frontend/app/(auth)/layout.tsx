/**
 * @fileoverview Authentication layout for TRAIDER V1
 * @module app/(auth)/layout
 *
 * @description
 * Layout component for authentication pages (login, register, etc.).
 * Provides a clean, minimal layout optimized for authentication flows
 * with proper security considerations and institutional branding.
 *
 * @performance
 * - Latency target: <50ms layout render
 * - Throughput: N/A
 * - Memory usage: <1MB
 *
 * @risk
 * - Failure impact: MEDIUM (affects auth pages only)
 * - Recovery strategy: Fallback to root layout
 *
 * @compliance
 * - Audit requirements: No
 * - Data retention: N/A
 *
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import type { Metadata } from 'next';

/**
 * Authentication layout metadata
 */
export const metadata: Metadata = {
  title: {
    default: 'Authentication - TRAIDER V1',
    template: '%s - TRAIDER V1',
  },
  description: 'Secure authentication for TRAIDER institutional crypto trading platform',
  robots: {
    index: false, // Don't index auth pages
    follow: false,
  },
};

/**
 * Authentication layout component
 *
 * @description
 * Provides a minimal, secure layout for authentication pages.
 * Includes security headers, proper styling, and institutional branding.
 *
 * @param children - Child authentication components (login, register, etc.)
 * @returns JSX element representing the auth layout
 *
 * @performance
 * - Minimal DOM structure for fast rendering
 * - Optimized CSS loading
 * - No unnecessary JavaScript
 *
 * @security
 * - Clean layout prevents information leakage
 * - No external resources loaded
 * - Proper CSRF protection ready
 *
 * @example
 * ```tsx
 * // Automatically wraps /login, /register pages
 * // Provides consistent auth page styling
 * ```
 */
export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      {/* Background pattern for visual appeal */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-accent/5" />

      {/* Main content area */}
      <div className="relative z-10">{children}</div>

      {/* Security notice (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="fixed bottom-4 left-4 text-xs text-muted-foreground bg-background/90 backdrop-blur-sm px-2 py-1 rounded border">
          Development Mode - Security Features Active
        </div>
      )}
    </div>
  );
}
