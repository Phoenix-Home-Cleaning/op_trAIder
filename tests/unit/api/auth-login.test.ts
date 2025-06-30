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

// Import the actual route handlers from unified API
import { POST, GET } from '../../../app/api/route';

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

  describe('POST /api - Authentication Flow (Unified API)', () => {
    /**
     * Test suite for POST login endpoint with unified route handler
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      // Verify token generation (updated for unified API)
      expect(data.token).toBeDefined();
      expect(typeof data.token).toBe('string');
      expect(data.token).toMatch(/^traider-jwt-/);
      
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      // Verify token generation (updated for unified API)
      expect(data.token).toBeDefined();
      expect(typeof data.token).toBe('string');
      expect(data.token).toMatch(/^traider-jwt-/);
      
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      const request = new NextRequest('http://localhost/api', {
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
      
      const request = new NextRequest('http://localhost/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: 'invalid json'
      });

      const response = await POST(request);
      const data = await response.json();

      // Verify error handling
      expect(response.status).toBe(500);
      expect(data.success).toBe(false);
      expect(data.message).toBe('Internal server error');
    });

    it('handles performance requirements', async () => {
      /**
       * Test that authentication endpoint responds within performance requirements
       * 
       * @performance Target: <200ms response time
       * @tradingImpact Fast authentication enables rapid user access
       * @riskLevel MEDIUM - Slow authentication affects user experience
       */
      
      const startTime = performance.now();
      
      const request = new NextRequest('http://localhost/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const response = await POST(request);
      const responseTime = performance.now() - startTime;

      // Should respond quickly
      expect(responseTime).toBeLessThan(300); // Generous threshold for test environment
      
      // Verify response is valid
      expect(response).toBeDefined();
      const data = await response.json();
      expect(data.success).toBe(true);
    });
  });

  describe('GET /api?endpoint=auth - Auth Info (Unified API)', () => {
    /**
     * Test suite for GET auth info endpoint
     * 
     * @description Tests authentication information endpoint
     * @riskLevel LOW - Information endpoint for API documentation
     */

    it('returns authentication endpoint information', async () => {
      /**
       * Test that auth info endpoint returns API documentation
       * 
       * @tradingImpact API discovery helps with integration and debugging
       * @riskLevel LOW - Informational endpoint for development
       */
      
      const request = new NextRequest('http://localhost/api?endpoint=auth');
      const response = await GET(request);
      const data = await response.json();

      // Verify auth info structure
      expect(data).toHaveProperty('endpoint');
      expect(data).toHaveProperty('methods');
      expect(data).toHaveProperty('version');
      expect(data).toHaveProperty('description');
      expect(data).toHaveProperty('phase');
      expect(data).toHaveProperty('demo_credentials');

      // Verify values
      expect(data.endpoint).toBe('/api?endpoint=auth');
      expect(data.methods).toContain('GET');
      expect(data.methods).toContain('POST');
      expect(data.version).toBe('1.0.0-alpha');
      expect(data.phase).toBe('Phase 0 - Demo Implementation');

      // Verify demo credentials information
      expect(data.demo_credentials).toHaveProperty('admin');
      expect(data.demo_credentials).toHaveProperty('demo');
      expect(data.demo_credentials.admin.role).toBe('administrator');
      expect(data.demo_credentials.demo.role).toBe('trader');
    });
  });
});

describe('Authentication Security Tests', () => {
  /**
   * Test suite for authentication security scenarios
   * 
   * @description Tests security-related authentication behavior
   * @riskLevel HIGH - Security tests are critical for system protection
   */

  it('does not leak sensitive information in error responses', async () => {
    /**
     * Test that error responses don't contain sensitive system information
     * 
     * @tradingImpact Information leakage could aid attackers
     * @riskLevel HIGH - Security information disclosure prevention
     */
    
    const request = new NextRequest('http://localhost/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'nonexistent',
        password: 'wrongpassword'
      })
    });

    const response = await POST(request);
    const data = await response.json();

    // Verify no sensitive information is leaked
    expect(data).not.toHaveProperty('stack');
    expect(data).not.toHaveProperty('code');
    expect(data).not.toHaveProperty('details');
    expect(data.message).not.toContain('database');
    expect(data.message).not.toContain('connection');
    expect(data.message).not.toContain('error');
  });

  it('maintains consistent response times for valid and invalid credentials', async () => {
    /**
     * Test that response times don't leak information about valid usernames
     * 
     * @tradingImpact Timing attacks could reveal valid usernames
     * @riskLevel MEDIUM - Timing attack prevention
     */
    
    // Test valid username, invalid password
    const validUserStart = performance.now();
    const validUserRequest = new NextRequest('http://localhost/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'admin',
        password: 'wrongpassword'
      })
    });
    await POST(validUserRequest);
    const validUserTime = performance.now() - validUserStart;

    // Test invalid username, invalid password
    const invalidUserStart = performance.now();
    const invalidUserRequest = new NextRequest('http://localhost/api', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'nonexistent',
        password: 'wrongpassword'
      })
    });
    await POST(invalidUserRequest);
    const invalidUserTime = performance.now() - invalidUserStart;

    // Response times should be similar (within 50ms)
    const timeDifference = Math.abs(validUserTime - invalidUserTime);
    expect(timeDifference).toBeLessThan(50);
  });

  it('handles concurrent authentication requests', async () => {
    /**
     * Test that concurrent authentication requests are handled properly
     * 
     * @tradingImpact Concurrent access should not cause authentication failures
     * @riskLevel MEDIUM - Concurrency handling for authentication
     */
    
    const requests = Array.from({ length: 5 }, () => 
      new NextRequest('http://localhost/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      })
    );

    // Execute all requests concurrently
    const promises = requests.map(request => POST(request));
    const responses = await Promise.all(promises);

    // All should succeed
    for (const response of responses) {
      expect(response.status).toBe(200);
      const data = await response.json();
      expect(data.success).toBe(true);
      expect(data.token).toBeDefined();
    }
  });
});
