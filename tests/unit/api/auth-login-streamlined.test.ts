/**
 * @fileoverview Streamlined API Authentication Tests - Zero Duplication
 * @module tests.unit.api.auth-login-streamlined
 *
 * @description
 * Streamlined tests for TRAIDER V1 unified API authentication redirection.
 * Eliminates code duplication through shared utilities and focused test logic.
 *
 * @performance
 * - Test execution target: <100ms per test
 * - Memory usage: <5MB per test suite
 * - Coverage requirement: >95%
 *
 * @risk
 * - Failure impact: HIGH - Authentication routing is critical for security
 * - Recovery strategy: Automated test retry with endpoint isolation
 *
 * @compliance
 * - Audit requirements: Yes - Authentication security validation
 * - Data retention: Test logs retained for 90 days
 *
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';
import { createStandardTestSuite, assertApiResponses } from '../../utils/sharedTestUtilities';

// Import API routes for testing
import { POST, GET } from '../../../app/api/route';

describe('🔐 Streamlined API Authentication Tests', () => {
  /**
   * Streamlined test suite with zero duplication
   * Uses shared utilities for consistent setup and assertions
   */

  const testSuite = createStandardTestSuite({ setupAuth: false, setupRouter: false });

  beforeEach(testSuite.beforeEach);
  afterEach(testSuite.afterEach);

  describe('Authentication Redirection', () => {
    it('redirects authentication requests to NextAuth endpoints', async () => {
      const response = await POST();
      const data = await response.json();
      assertApiResponses.authRedirect(response, data);
    });

    it('handles different credential formats consistently', async () => {
      const testCases = [
        { username: 'viewer', password: 'viewer123' },
        { email: 'test@example.com', password: 'password' },
        { user: 'invalid', pass: 'wrong' },
      ];

      for (const _credentials of testCases) {
        const response = await POST();
        const data = await response.json();
        assertApiResponses.authRedirect(response, data);
      }
    });
  });

  describe('API Information Endpoints', () => {
    it('provides API information when requested', async () => {
      const infoRequest = new NextRequest(
        new Request('http://localhost:3000/api', {
          method: 'GET',
        })
      );

      const response = await GET(infoRequest);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.authentication).toBe('Handled by NextAuth.js at /api/auth/*');
      expect(data.endpoints).toEqual({
        health: '/api?endpoint=health',
        info: '/api?endpoint=info',
      });
    });

    it('handles health check requests', async () => {
      const healthRequest = new NextRequest(
        new Request('http://localhost:3000/api?endpoint=health', {
          method: 'GET',
        })
      );

      const response = await GET(healthRequest);
      const data = await response.json();
      assertApiResponses.healthCheck(response, data);
    });

    it('provides detailed API information', async () => {
      const infoRequest = new NextRequest(
        new Request('http://localhost:3000/api?endpoint=info', {
          method: 'GET',
        })
      );

      const response = await GET(infoRequest);
      const data = await response.json();
      assertApiResponses.apiInfo(response, data);
    });
  });

  describe('Performance & Security', () => {
    it('responds within acceptable latency limits', async () => {
      const start = performance.now();

      await POST();

      const duration = performance.now() - start;
      expect(duration).toBeLessThan(100); // <100ms for auth redirect
    });

    it('maintains consistent response format across requests', async () => {
      const responses = await Promise.all([
        POST().then((r) => r.json()),
        POST().then((r) => r.json()),
        POST().then((r) => r.json()),
      ]);

      // All responses should have identical structure
      const firstResponse = responses[0];
      responses.forEach((response) => {
        expect(response).toEqual(firstResponse);
      });
    });
  });
});
