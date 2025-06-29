/**
 * @fileoverview Login API Endpoint Integration Tests
 * @module tests.unit.api.auth-login
 * 
 * @description
 * Comprehensive integration tests for the TRAIDER V1 login authentication API endpoint.
 * Tests actual route handlers to achieve 90%+ statement coverage for world-class
 * engineering standards. Includes authentication flows, error handling, and security validation.
 * 
 * @performance
 * - Test execution target: <200ms per test
 * - Memory usage: <5MB per test suite
 * - Coverage requirement: >95%
 * 
 * @risk
 * - Failure impact: HIGH - Authentication is critical for security
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

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';

// Import the actual route handlers
import { POST, GET } from '../../../app/api/auth/login/route';

describe('Login API Endpoint - Integration Tests', () => {
  /**
   * Test suite for login API endpoint functionality with real route handlers
   * 
   * @description Tests actual authentication responses and security validation
   * @riskLevel HIGH - Authentication is critical for system security
   */
  
  beforeEach(() => {
    // Reset environment for each test
    vi.clearAllMocks();
    
    // Set test environment
    vi.stubEnv('NODE_ENV', 'test');
  });

  afterEach(() => {
    // Clean up any environment changes
    vi.restoreAllMocks();
  });

  describe('POST /api/auth/login - Authentication Flow', () => {
    /**
     * Test suite for POST login endpoint with actual route handler
     * 
     * @description Tests authentication flows with real credential validation
     * @riskLevel HIGH - Authentication security is critical
     */

    it('authenticates admin user with valid credentials', async () => {
      /**
       * Test successful admin authentication
       * 
       * @performance Target: <200ms response time
       * @tradingImpact Admin access enables full trading platform management
       * @riskLevel HIGH - Admin credentials provide elevated access
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify successful authentication
      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.message).toBe('Authentication successful');
      
      // Verify token generation
      expect(data.token).toBeDefined();
      expect(typeof data.token).toBe('string');
      expect(data.token).toMatch(/^placeholder-jwt-token-/);
      
      // Verify user data
      expect(data.user).toBeDefined();
      expect(data.user.id).toBe('1');
      expect(data.user.username).toBe('admin');
      expect(data.user.role).toBe('administrator');
    });

    it('authenticates demo user with valid credentials', async () => {
      /**
       * Test successful demo user authentication
       * 
       * @performance Target: <200ms response time
       * @tradingImpact Demo access enables trading platform testing
       * @riskLevel MEDIUM - Demo credentials provide limited access
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'demo',
          password: 'demo123'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify successful authentication
      expect(response.status).toBe(200);
      expect(data.success).toBe(true);
      expect(data.message).toBe('Authentication successful');
      
      // Verify token generation
      expect(data.token).toBeDefined();
      expect(typeof data.token).toBe('string');
      expect(data.token).toMatch(/^placeholder-jwt-token-/);
      
      // Verify user data
      expect(data.user).toBeDefined();
      expect(data.user.id).toBe('2');
      expect(data.user.username).toBe('demo');
      expect(data.user.role).toBe('trader');
    });

    it('rejects invalid credentials', async () => {
      /**
       * Test authentication failure with invalid credentials
       * 
       * @tradingImpact Invalid credentials must be rejected to maintain security
       * @riskLevel HIGH - Authentication security prevents unauthorized access
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'invalid',
          password: 'wrong'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify authentication failure
      expect(response.status).toBe(401);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Invalid username or password');
      
      // Verify no sensitive data in response
      expect(data.token).toBeUndefined();
      expect(data.user).toBeUndefined();
    });

    it('validates required username field', async () => {
      /**
       * Test input validation for missing username
       * 
       * @tradingImpact Input validation prevents malformed authentication attempts
       * @riskLevel MEDIUM - Input validation is essential for security
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          password: 'password'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify validation error
      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Username and password are required');
      
      // Verify no authentication data in response
      expect(data.token).toBeUndefined();
      expect(data.user).toBeUndefined();
    });

    it('validates required password field', async () => {
      /**
       * Test input validation for missing password
       * 
       * @tradingImpact Input validation prevents malformed authentication attempts
       * @riskLevel MEDIUM - Input validation is essential for security
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify validation error
      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Username and password are required');
      
      // Verify no authentication data in response
      expect(data.token).toBeUndefined();
      expect(data.user).toBeUndefined();
    });

    it('validates both username and password fields', async () => {
      /**
       * Test input validation for missing both fields
       * 
       * @tradingImpact Input validation prevents malformed authentication attempts
       * @riskLevel MEDIUM - Input validation is essential for security
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({})
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify validation error
      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Username and password are required');
    });

    it('handles empty string credentials', async () => {
      /**
       * Test validation with empty string credentials
       * 
       * @tradingImpact Empty credentials should be treated as missing
       * @riskLevel MEDIUM - Edge case validation for security
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: '',
          password: ''
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify validation error for empty strings
      expect(response.status).toBe(400);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Username and password are required');
    });

    it('handles malformed JSON request', async () => {
      /**
       * Test error handling for malformed JSON requests
       * 
       * @tradingImpact Malformed requests should be handled gracefully
       * @riskLevel MEDIUM - Error handling prevents server crashes
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid-json'
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify error handling
      expect(response.status).toBe(500);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Internal server error');
      
      // Verify no sensitive data in error response
      expect(data.token).toBeUndefined();
      expect(data.user).toBeUndefined();
    });

    it('generates unique tokens for multiple logins', async () => {
      /**
       * Test that each successful login generates a unique token
       * 
       * @tradingImpact Unique tokens prevent session hijacking
       * @riskLevel HIGH - Token uniqueness is critical for security
       */
      
      const request1 = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const request2 = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const response1 = await POST(request1);
      const data1 = await response1.json();
      
      // Small delay to ensure different timestamps
      await new Promise(resolve => setTimeout(resolve, 1));
      
      const response2 = await POST(request2);
      const data2 = await response2.json();

      // Verify both logins succeeded
      expect(data1.success).toBe(true);
      expect(data2.success).toBe(true);
      
      // Verify tokens are unique
      expect(data1.token).not.toBe(data2.token);
      expect(data1.token).toBeDefined();
      expect(data2.token).toBeDefined();
    });

    it('handles performance requirements', async () => {
      /**
       * Test that login endpoint responds within performance requirements
       * 
       * @performance Target: <200ms response time
       * @tradingImpact Fast authentication enables quick platform access
       * @riskLevel MEDIUM - Performance affects user experience
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const startTime = performance.now();
      const response = await POST(request);
      const responseTime = performance.now() - startTime;

      // Should respond quickly
      expect(responseTime).toBeLessThan(200);
      
      // Verify response is valid
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
    });
  });

  describe('GET /api/auth/login - API Information', () => {
    /**
     * Test suite for GET login endpoint with actual route handler
     * 
     * @description Tests API information endpoint for documentation and discovery
     * @riskLevel LOW - Informational endpoint only
     */

    it('returns API endpoint information', async () => {
      /**
       * Test that GET endpoint returns comprehensive API information
       * 
       * @performance Target: <50ms response time
       * @tradingImpact API documentation enables proper integration
       * @riskLevel LOW - Informational endpoint with no sensitive data
       */
      
      const response = await GET();
      const data = await response.json();

      // Verify response structure
      expect(response.status).toBe(200);
      expect(data.endpoint).toBe('/api/auth/login');
      expect(data.method).toBe('POST');
      expect(data.description).toBe('User authentication endpoint');
      expect(data.version).toBe('1.0.0-alpha');
      expect(data.status).toBe('active');
      expect(data.phase).toBe('Phase 0 - Placeholder Implementation');
      
      // Verify demo credentials are included
      expect(data.demo_credentials).toBeDefined();
      expect(data.demo_credentials.admin).toBeDefined();
      expect(data.demo_credentials.demo).toBeDefined();
      
      // Verify demo credential structure
      expect(data.demo_credentials.admin.username).toBe('admin');
      expect(data.demo_credentials.admin.password).toBe('password');
      expect(data.demo_credentials.demo.username).toBe('demo');
      expect(data.demo_credentials.demo.password).toBe('demo123');
    });

    it('handles performance requirements for GET endpoint', async () => {
      /**
       * Test that GET endpoint responds within performance requirements
       * 
       * @performance Target: <50ms response time
       * @tradingImpact Fast API documentation access
       * @riskLevel LOW - Performance for informational endpoint
       */
      
      const startTime = performance.now();
      const response = await GET();
      const responseTime = performance.now() - startTime;

      // Should respond very quickly for static information
      expect(responseTime).toBeLessThan(50);
      
      // Verify response is valid
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.endpoint).toBeDefined();
    });

    it('returns consistent API information structure', async () => {
      /**
       * Test that API information has consistent structure and types
       * 
       * @tradingImpact Consistent API information enables reliable integration
       * @riskLevel LOW - Structure validation for API documentation
       */
      
      const response = await GET();
      const data = await response.json();

      // Verify all fields have correct types
      expect(typeof data.endpoint).toBe('string');
      expect(typeof data.method).toBe('string');
      expect(typeof data.description).toBe('string');
      expect(typeof data.version).toBe('string');
      expect(typeof data.status).toBe('string');
      expect(typeof data.phase).toBe('string');
      expect(typeof data.demo_credentials).toBe('object');
      
      // Verify nested structures
      expect(typeof data.demo_credentials.admin).toBe('object');
      expect(typeof data.demo_credentials.demo).toBe('object');
      expect(typeof data.demo_credentials.admin.username).toBe('string');
      expect(typeof data.demo_credentials.admin.password).toBe('string');
      expect(typeof data.demo_credentials.demo.username).toBe('string');
      expect(typeof data.demo_credentials.demo.password).toBe('string');
    });
  });

  describe('Security and Edge Cases', () => {
    /**
     * Test suite for security validation and edge case handling
     * 
     * @description Tests security aspects and edge cases
     * @riskLevel HIGH - Security testing is critical
     */

    it('does not expose sensitive information in error responses', async () => {
      /**
       * Test that error responses don't leak sensitive information
       * 
       * @tradingImpact Error responses must not expose system internals
       * @riskLevel HIGH - Information disclosure could aid attackers
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'invalid',
          password: 'wrong'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify error response doesn't contain sensitive data
      expect(data.token).toBeUndefined();
      expect(data.user).toBeUndefined();
      
      // Verify error message is generic
      expect(data.message).toBe('Invalid username or password');
      expect(data.message).not.toContain('database');
      expect(data.message).not.toContain('sql');
      expect(data.message).not.toContain('error');
    });

    it('handles case sensitivity in usernames', async () => {
      /**
       * Test username case sensitivity for security
       * 
       * @tradingImpact Case sensitivity prevents username enumeration
       * @riskLevel MEDIUM - Username validation security
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'ADMIN',
          password: 'password'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify case-sensitive username handling
      expect(response.status).toBe(401);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Invalid username or password');
    });

    it('validates token format consistency', async () => {
      /**
       * Test that generated tokens follow consistent format
       * 
       * @tradingImpact Consistent token format enables proper validation
       * @riskLevel MEDIUM - Token format consistency for security
       */
      
      const request = new NextRequest('http://localhost/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify token format
      expect(data.token).toMatch(/^placeholder-jwt-token-\d+-[a-z0-9]+$/);
      expect(data.token.length).toBeGreaterThan(30); // Ensure sufficient length
    });
  });
});
