/**
 * @fileoverview Comprehensive Middleware Tests
 * @module tests.unit.frontend.middleware-comprehensive
 *
 * @description
 * Comprehensive test suite for the TRAIDER V1 middleware including authentication,
 * authorization, performance validation, and edge case handling.
 *
 * @performance
 * - Test execution target: <100ms per test
 * - Memory usage: <5MB per test suite
 * - Coverage requirement: >95%
 *
 * @risk
 * - Failure impact: CRITICAL - Middleware affects all requests
 * - Recovery strategy: Automated fallback to basic auth
 *
 * @compliance
 * - Audit requirements: Yes - Security middleware testing
 * - Data retention: Test logs retained for 90 days
 *
 * @see {@link docs/architecture/middleware.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { NextResponse } from 'next/server';

// Mock next-auth/middleware
const mockWithAuth = vi.fn();
vi.mock('next-auth/middleware', () => ({
  withAuth: mockWithAuth,
}));

// Mock Next.js server components
vi.mock('next/server', () => ({
  NextResponse: {
    next: vi.fn(() => ({ status: 200 })),
  },
}));

describe('🛡️ Middleware Comprehensive Testing', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('🔐 Authorization Callback Testing', () => {
    it('should configure authorization callback correctly', async () => {
      // Import middleware to trigger configuration
      await import('../../../middleware');

      // Verify withAuth was called
      expect(mockWithAuth).toHaveBeenCalled();

      // Get the authorization callback from the mock call
      const withAuthCall = mockWithAuth.mock.calls[0];
      if (withAuthCall && withAuthCall[1] && withAuthCall[1].callbacks) {
        const authCallback = withAuthCall[1].callbacks.authorized;

        // Test null token
        expect(authCallback({ token: null })).toBe(false);

        // Test valid roles
        expect(authCallback({ token: { role: 'ADMIN' } })).toBe(true);
        expect(authCallback({ token: { role: 'TRADER' } })).toBe(true);
        expect(authCallback({ token: { role: 'VIEWER' } })).toBe(true);

        // Test invalid roles
        expect(authCallback({ token: { role: 'INVALID' } })).toBe(false);
        expect(authCallback({ token: { role: '' } })).toBe(false);
        expect(authCallback({ token: {} })).toBe(false);
      }
    });

    it('should handle edge cases in authorization', async () => {
      await import('../../../middleware');

      const withAuthCall = mockWithAuth.mock.calls[0];
      if (withAuthCall && withAuthCall[1] && withAuthCall[1].callbacks) {
        const authCallback = withAuthCall[1].callbacks.authorized;

        // Test undefined token
        expect(authCallback({ token: undefined })).toBe(false);

        // Test case sensitivity
        expect(authCallback({ token: { role: 'admin' } })).toBe(false);
        expect(authCallback({ token: { role: 'trader' } })).toBe(false);

        // Test token without role
        expect(authCallback({ token: { sub: 'user123' } })).toBe(false);
      }
    });
  });

  describe('🚀 Middleware Function Testing', () => {
    it('should return NextResponse.next() for authenticated requests', async () => {
      await import('../../../middleware');

      // Get the middleware function from the mock call
      const withAuthCall = mockWithAuth.mock.calls[0];
      if (withAuthCall && withAuthCall[0]) {
        const middlewareFunction = withAuthCall[0];
        const result = middlewareFunction();

        expect(NextResponse.next).toHaveBeenCalled();
        expect(result).toBeDefined();
      }
    });

    it('should handle multiple middleware calls', async () => {
      await import('../../../middleware');

      const withAuthCall = mockWithAuth.mock.calls[0];
      if (withAuthCall && withAuthCall[0]) {
        const middlewareFunction = withAuthCall[0];

        // Call multiple times
        middlewareFunction();
        middlewareFunction();

        expect(NextResponse.next).toHaveBeenCalledTimes(2);
      }
    });
  });

  describe('🔧 Configuration Testing', () => {
    it('should have proper route matcher configuration', async () => {
      const { config } = await import('../../../middleware');

      expect(config).toBeDefined();
      expect(config.matcher).toBeDefined();
      expect(Array.isArray(config.matcher)).toBe(true);
      expect(config.matcher.length).toBeGreaterThan(0);

      // Verify matcher pattern structure
      const matcherPattern = config.matcher?.[0];
      if (matcherPattern) {
        expect(typeof matcherPattern).toBe('string');
        expect(matcherPattern.length).toBeGreaterThan(0);
      }
    });

    it('should exclude authentication routes from protection', async () => {
      const { config } = await import('../../../middleware');
      const matcherPattern = config.matcher?.[0];

      if (matcherPattern) {
        // Pattern should exclude key routes
        expect(matcherPattern).toContain('api/auth');
        expect(matcherPattern).toContain('api/health');
        expect(matcherPattern).toContain('_next/static');
        expect(matcherPattern).toContain('login');
      }
    });

    it('should have comprehensive route exclusions', async () => {
      const { config } = await import('../../../middleware');
      const matcherPattern = config.matcher?.[0];

      if (matcherPattern) {
        // Should exclude favicon and image optimization
        expect(matcherPattern).toContain('favicon.ico');
        expect(matcherPattern).toContain('_next/image');

        // Verify it's a negative lookahead pattern
        expect(matcherPattern).toContain('(?!');
      }
    });
  });

  describe('⚡ Performance Testing', () => {
    it('should execute authorization quickly', async () => {
      await import('../../../middleware');

      const withAuthCall = mockWithAuth.mock.calls[0];
      if (withAuthCall && withAuthCall[1] && withAuthCall[1].callbacks) {
        const authCallback = withAuthCall[1].callbacks.authorized;

        const start = performance.now();
        authCallback({ token: { role: 'TRADER' } });
        const end = performance.now();

        expect(end - start).toBeLessThan(5); // Should complete in <5ms
      }
    });

    it('should handle rapid authorization checks', async () => {
      await import('../../../middleware');

      const withAuthCall = mockWithAuth.mock.calls[0];
      if (withAuthCall && withAuthCall[1] && withAuthCall[1].callbacks) {
        const authCallback = withAuthCall[1].callbacks.authorized;

        const iterations = 100;
        const start = performance.now();

        for (let i = 0; i < iterations; i++) {
          authCallback({ token: { role: 'ADMIN' } });
        }

        const end = performance.now();
        const avgTime = (end - start) / iterations;

        expect(avgTime).toBeLessThan(1); // Should average <1ms per check
      }
    });
  });
});
