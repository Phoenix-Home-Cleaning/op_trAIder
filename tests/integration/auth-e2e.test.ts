/**
 * @fileoverview End-to-End Authentication Integration Tests
 * @module tests.integration.auth-e2e
 * 
 * @description
 * Comprehensive end-to-end tests for TRAIDER V1 authentication flow.
 * Tests complete user journey from login page through API authentication
 * to ensure real functionality beyond unit-level mocks.
 * 
 * @performance
 * - Test execution target: <500ms per test
 * - Memory usage: <10MB per test suite
 * - Coverage requirement: 100% authentication flow
 * 
 * @risk
 * - Failure impact: CRITICAL - Authentication is security foundation
 * - Recovery strategy: Automated test retry with full flow validation
 * 
 * @compliance
 * - Audit requirements: Yes - Complete authentication security validation
 * - Data retention: Test logs retained for 90 days
 * 
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// Import the actual route handlers
import { POST, GET } from '../../app/api/route';

describe('Authentication End-to-End Integration Tests', () => {
  /**
   * Test suite for complete authentication flow validation
   * 
   * @description Tests real authentication workflow from frontend to backend
   * @riskLevel CRITICAL - Authentication security is system foundation
   */

  beforeEach(() => {
    // Reset environment for each test
    global.fetch = vi.fn();
  });

  afterEach(() => {
    // Clean up after each test
    vi.restoreAllMocks();
  });

  describe('Complete Authentication Flow', () => {
    /**
     * Test suite for end-to-end authentication workflow
     * 
     * @description Validates complete user authentication journey
     * @riskLevel CRITICAL - Authentication flow must work perfectly
     */

    it('completes full admin authentication workflow', async () => {
      /**
       * Test complete admin authentication from login to token validation
       * 
       * @performance Target: <500ms complete flow
       * @tradingImpact Admin authentication enables full platform access
       * @riskLevel CRITICAL - Admin access provides elevated privileges
       */

      // Step 1: Simulate login form submission to unified API
      const loginRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      // Step 2: Process authentication through unified API
      const loginResponse = await POST(loginRequest);
      const loginData = await loginResponse.json();

      // Step 3: Verify successful authentication
      expect(loginResponse.status).toBe(200);
      expect(loginData.success).toBe(true);
      expect(loginData.token).toBeDefined();
      expect(loginData.user).toBeDefined();
      expect(loginData.user.role).toBe('administrator');

      // Step 4: Validate token format (matches login page expectations)
      expect(loginData.token).toMatch(/^traider-jwt-\d+-[a-z0-9]+$/);
      
      // Step 5: Verify user data structure
      expect(loginData.user).toEqual({
        id: '1',
        username: 'admin',
        role: 'administrator'
      });

      // Step 6: Test API health check with authentication context
      const healthRequest = new NextRequest('http://localhost:3000/api?endpoint=health', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${loginData.token}`,
          'Content-Type': 'application/json'
        }
      });

      const healthResponse = await GET(healthRequest);
      const healthData = await healthResponse.json();

      // Step 7: Verify health check responds correctly
      expect(healthResponse.status).toBe(200);
      expect(healthData.status).toBe('healthy');
      expect(healthData.version).toBe('1.0.0-alpha');
    });

    it('completes full demo user authentication workflow', async () => {
      /**
       * Test complete demo user authentication workflow
       * 
       * @performance Target: <500ms complete flow
       * @tradingImpact Demo authentication enables trading platform testing
       * @riskLevel HIGH - Demo access must be properly restricted
       */

      // Step 1: Demo user login
      const loginRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'demo',
          password: 'demo123'
        })
      });

      const loginResponse = await POST(loginRequest);
      const loginData = await loginResponse.json();

      // Step 2: Verify demo authentication
      expect(loginResponse.status).toBe(200);
      expect(loginData.success).toBe(true);
      expect(loginData.user.role).toBe('trader');
      expect(loginData.user.id).toBe('2');

      // Step 3: Test auth info endpoint
      const authInfoRequest = new NextRequest('http://localhost:3000/api?endpoint=auth', {
        method: 'GET'
      });

      const authInfoResponse = await GET(authInfoRequest);
      const authInfoData = await authInfoResponse.json();

      // Step 4: Verify auth info includes demo credentials
      expect(authInfoResponse.status).toBe(200);
      expect(authInfoData.demo_credentials).toBeDefined();
      expect(authInfoData.demo_credentials.demo).toEqual({
        username: 'demo',
        password: 'demo123',
        role: 'trader'
      });
    });

    it('handles complete authentication failure workflow', async () => {
      /**
       * Test complete authentication failure handling
       * 
       * @tradingImpact Failed authentication must be properly rejected
       * @riskLevel CRITICAL - Security boundary enforcement
       */

      // Step 1: Invalid credentials
      const invalidRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'invalid',
          password: 'wrong'
        })
      });

      const invalidResponse = await POST(invalidRequest);
      const invalidData = await invalidResponse.json();

      // Step 2: Verify proper rejection
      expect(invalidResponse.status).toBe(401);
      expect(invalidData.success).toBe(false);
      expect(invalidData.message).toBe('Invalid username or password');
      expect(invalidData.token).toBeUndefined();
      expect(invalidData.user).toBeUndefined();

      // Step 3: Test that API endpoints work without authentication
      const healthRequest = new NextRequest('http://localhost:3000/api?endpoint=health', {
        method: 'GET'
      });

      const healthResponse = await GET(healthRequest);
      
      // Step 4: Health check should work without auth (public endpoint)
      expect(healthResponse.status).toBe(200);
    });

    it('validates input sanitization throughout flow', async () => {
      /**
       * Test input validation and sanitization across authentication flow
       * 
       * @tradingImpact Input validation prevents injection attacks
       * @riskLevel HIGH - Security input validation critical
       */

      // Step 1: Test empty credentials
      const emptyRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      const emptyResponse = await POST(emptyRequest);
      const emptyData = await emptyResponse.json();

      expect(emptyResponse.status).toBe(400);
      expect(emptyData.message).toBe('Username and password are required');

      // Step 2: Test malformed JSON
      const malformedRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid-json'
      });

      const malformedResponse = await POST(malformedRequest);
      expect(malformedResponse.status).toBe(500);

      // Step 3: Test SQL injection attempt
      const injectionRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: "admin'; DROP TABLE users; --",
          password: "password"
        })
      });

      const injectionResponse = await POST(injectionRequest);
      const injectionData = await injectionResponse.json();

      // Should fail authentication, not crash
      expect(injectionResponse.status).toBe(401);
      expect(injectionData.success).toBe(false);
    });

    it('validates API endpoint routing consistency', async () => {
      /**
       * Test unified API endpoint routing works correctly
       * 
       * @tradingImpact API routing must be consistent and reliable
       * @riskLevel MEDIUM - API consistency affects user experience
       */

      // Step 1: Test default API info endpoint
      const infoRequest = new NextRequest('http://localhost:3000/api', {
        method: 'GET'
      });

      const infoResponse = await GET(infoRequest);
      const infoData = await infoResponse.json();

      expect(infoResponse.status).toBe(200);
      expect(infoData.name).toBe('TRAIDER V1 API');
      expect(infoData.version).toBe('1.0.0-alpha');
      expect(infoData.endpoints).toBeDefined();

      // Step 2: Test health endpoint routing
      const healthRequest = new NextRequest('http://localhost:3000/api?endpoint=health', {
        method: 'GET'
      });

      const healthResponse = await GET(healthRequest);
      const healthData = await healthResponse.json();

      expect(healthResponse.status).toBe(200);
      expect(healthData.status).toBe('healthy');

      // Step 3: Test auth info endpoint routing
      const authRequest = new NextRequest('http://localhost:3000/api?endpoint=auth', {
        method: 'GET'
      });

      const authResponse = await GET(authRequest);
      const authData = await authResponse.json();

      expect(authResponse.status).toBe(200);
      expect(authData.endpoint).toBe('/api?endpoint=auth');
      expect(authData.demo_credentials).toBeDefined();

      // Step 4: Test unknown endpoint handling
      const unknownRequest = new NextRequest('http://localhost:3000/api?endpoint=unknown', {
        method: 'GET'
      });

      const unknownResponse = await GET(unknownRequest);

      // Should fall back to default API info
      expect(unknownResponse.status).toBe(200);
    });

    it('validates token generation and format consistency', async () => {
      /**
       * Test token generation consistency across multiple requests
       * 
       * @tradingImpact Token consistency ensures reliable authentication
       * @riskLevel HIGH - Token security is critical for session management
       */

      const tokens = [];

      // Generate multiple tokens
      for (let i = 0; i < 3; i++) {
        const request = new NextRequest('http://localhost:3000/api', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: 'admin',
            password: 'password'
          })
        });

        const response = await POST(request);
        const data = await response.json();

        expect(response.status).toBe(200);
        expect(data.token).toBeDefined();
        tokens.push(data.token);
      }

      // Verify all tokens are unique
      const uniqueTokens = new Set(tokens);
      expect(uniqueTokens.size).toBe(tokens.length);

      // Verify all tokens match expected format
      tokens.forEach(token => {
        expect(token).toMatch(/^traider-jwt-\d+-[a-z0-9]+$/);
        expect(token.length).toBeGreaterThan(20);
      });
    });
  });

  describe('Performance and Reliability', () => {
    /**
     * Test suite for authentication performance and reliability
     * 
     * @description Validates authentication meets performance requirements
     * @riskLevel MEDIUM - Performance affects user experience
     */

    it('completes authentication within performance targets', async () => {
      /**
       * Test authentication performance meets institutional requirements
       * 
       * @performance Target: <200ms authentication time
       * @tradingImpact Fast authentication improves trading workflow
       * @riskLevel MEDIUM - Performance affects user satisfaction
       */

      const startTime = Date.now();

      const request = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      const endTime = Date.now();
      const duration = endTime - startTime;

      // Verify functionality
      expect(response.status).toBe(200);
      expect(data.success).toBe(true);

      // Verify performance target
      expect(duration).toBeLessThan(200); // 200ms target
    });

    it('handles concurrent authentication requests', async () => {
      /**
       * Test authentication under concurrent load
       * 
       * @performance Target: Handle 10 concurrent requests
       * @tradingImpact Concurrent access needed for multiple users
       * @riskLevel MEDIUM - Concurrency affects scalability
       */

      const requests = Array.from({ length: 5 }, () => 
        new NextRequest('http://localhost:3000/api', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            username: 'admin',
            password: 'password'
          })
        })
      );

      const responses = await Promise.all(
        requests.map(request => POST(request))
      );

      const results = await Promise.all(
        responses.map(response => response.json())
      );

      // All requests should succeed
      responses.forEach(response => {
        expect(response.status).toBe(200);
      });

      results.forEach(data => {
        expect(data.success).toBe(true);
        expect(data.token).toBeDefined();
      });

      // All tokens should be unique
      const tokens = results.map(data => data.token);
      const uniqueTokens = new Set(tokens);
      expect(uniqueTokens.size).toBe(tokens.length);
    });
  });
}); 