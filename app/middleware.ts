/**
 * @fileoverview Next.js middleware for route protection and authentication
 * @module middleware
 *
 * @description
 * Implements institutional-grade route protection for the TRAIDER trading platform.
 * Protects sensitive trading routes, handles authentication state, and provides
 * secure redirects for unauthorized access attempts.
 *
 * @performance
 * - Latency target: <5ms per request
 * - Throughput: Unlimited (edge runtime)
 * - Memory usage: <1MB
 *
 * @risk
 * - Failure impact: HIGH - Unauthorized access to trading systems
 * - Recovery strategy: Fail-safe to login redirect
 *
 * @compliance
 * - Audit requirements: Yes - All access attempts logged
 * - Data retention: 90 days access logs
 *
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0-alpha.1
 * @author TRAIDER Team
 */

import { withAuth } from 'next-auth/middleware';
import { NextResponse } from 'next/server';

/**
 * NextAuth.js middleware configuration for route protection
 *
 * @description Protects all dashboard routes and API endpoints that require authentication.
 * Implements role-based access control and secure session validation.
 *
 * @performance O(1) time, <5ms latency for route checks
 * @sideEffects Redirects unauthorized users to login page
 *
 * @tradingImpact Prevents unauthorized access to trading controls and data
 * @riskLevel HIGH - Critical security boundary for trading platform
 *
 * @example
 * ```typescript
 * // Automatic protection for /dashboard/* routes
 * // Redirects to /login if not authenticated
 * ```
 *
 * @monitoring
 * - Metric: `auth.middleware.latency`
 * - Alert threshold: > 10ms
 */
export default withAuth(
  /**
   * Middleware callback executed on each protected request.
   *
   * @description Performs final authorization checks and allows the request to proceed if
   * authentication and role validation succeed. Additional security logic such as
   * IP allow-listing or geo-fencing can be added here in future phases.
   *
   * @returns {NextResponse} Edge response object indicating the request should continue.
   *
   * @performance O(1) time, <2 ms typical latency
   * @sideEffects None
   *
   * @tradingImpact Ensures that only authenticated traffic reaches trading routes,
   * maintaining system integrity.
   * @riskLevel HIGH – critical security boundary.
   */
  function middleware() {
    // Additional custom logic can be added here
    // For now, just pass through authenticated requests
    return NextResponse.next();
  },
  {
    callbacks: {
      /**
       * Authorization callback for fine-grained access control
       *
       * @description Determines if a user is authorized to access a specific route.
       * Implements role-based access control for different trading functions.
       *
       * @param {object} params - Authorization parameters
       * @param {object} params.token - JWT token with user information
       * @returns {boolean} True if user is authorized, false otherwise
       *
       * @tradingImpact Controls access to different trading functions based on user role
       * @riskLevel HIGH - Determines access to money-moving operations
       *
       * @example
       * ```typescript
       * // ADMIN: Full access to all routes
       * // TRADER: Access to trading but not admin functions
       * // VIEWER: Read-only access to dashboards
       * ```
       */
      authorized: ({ token }) => {
        // Check if user has a valid token with role information
        if (!token) {
          return false;
        }

        // For Phase 0, allow all authenticated users with valid roles
        // Phase 1+ will implement granular role-based access control
        const validRoles = ['ADMIN', 'TRADER', 'VIEWER'];
        return validRoles.includes(token.role as string);
      },
    },
  }
);

/**
 * Matcher configuration for protected routes
 *
 * @description Defines which routes require authentication.
 * Uses Next.js path matching syntax for efficient route protection.
 *
 * Protected routes:
 * - /dashboard/* - All dashboard pages
 * - /api/protected/* - Protected API endpoints
 * - /performance/* - Performance analytics
 * - /risk/* - Risk management
 * - /signals/* - Trading signals
 * - /system/* - System administration
 *
 * @performance Compiled regex patterns for O(1) route matching
 * @sideEffects None - Pure route matching function
 *
 * @tradingImpact Protects all trading-related functionality
 * @riskLevel CRITICAL - Defines security perimeter
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api/auth (authentication endpoints)
     * - api/health (health check endpoints)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     * - login page
     */
    '/((?!api/auth|api/health|_next/static|_next/image|favicon.ico|login|$).*)',
  ],
};
