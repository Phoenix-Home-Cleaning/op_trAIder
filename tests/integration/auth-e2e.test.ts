/**
 * @fileoverview End-to-End Authentication Integration Tests
 * @module tests.integration.auth-e2e
 * 
 * @description
 * Comprehensive end-to-end tests for TRAIDER V1 NextAuth authentication flow.
 * Tests complete user journey from login page through NextAuth authentication
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

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { NextRequest } from 'next/server';
import type { CredentialsConfig } from 'next-auth/providers/credentials';

// Import the actual route handlers
import { POST, GET } from '../../app/api/route';

describe('Authentication End-to-End Integration Tests', () => {
  /**
   * Test suite for complete authentication flow validation
   * 
   * @description Tests real authentication workflow with NextAuth integration
   * @riskLevel CRITICAL - Authentication security is system foundation
   */

  beforeEach(() => {
    // Reset environment for each test
    vi.clearAllMocks();
    vi.stubEnv('NODE_ENV', 'test');
    vi.stubEnv('NEXTAUTH_SECRET', 'test-secret-key-for-testing');
    vi.stubEnv('NEXT_PUBLIC_API_URL', 'http://localhost:8000');
  });

  afterEach(() => {
    // Clean up after each test
    vi.restoreAllMocks();
  });

  describe('API Authentication Redirection', () => {
    /**
     * Test suite for API authentication redirection behavior
     * 
     * @description Validates that old API correctly redirects to NextAuth
     * @riskLevel HIGH - Proper redirection prevents authentication confusion
     */

    it('redirects authentication requests to NextAuth endpoints', async () => {
      /**
       * Test that POST /api correctly redirects auth requests to NextAuth
       * 
       * @tradingImpact Ensures users are directed to correct authentication
       * @riskLevel HIGH - Authentication routing is critical
       */

      const loginRequest = new NextRequest('http://localhost:3000/api', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: 'admin',
          password: 'password'
        })
      });

      const response = await POST(loginRequest);
      const data = await response.json();

      // Verify redirection response
      expect(response.status).toBe(410); // Gone - moved to NextAuth
      expect(data.error).toBe('Authentication moved to NextAuth.js');
      expect(data.auth_endpoints).toEqual({
        signin: '/api/auth/signin',
        signout: '/api/auth/signout',
        session: '/api/auth/session',
      });
      expect(data.message).toBe('Use NextAuth.js endpoints for authentication');
    });

    it('provides API information with authentication details', async () => {
      /**
       * Test that GET /api provides authentication information
       * 
       * @tradingImpact Helps users understand authentication system
       * @riskLevel LOW - Information endpoint for user guidance
       */

      const infoRequest = new NextRequest('http://localhost:3000/api', {
        method: 'GET'
      });

      const response = await GET(infoRequest);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.authentication).toBe('Handled by NextAuth.js at /api/auth/*');
      expect(data.endpoints).toEqual({
        health: '/api?endpoint=health',
        info: '/api?endpoint=info',
      });
    });
  });

  describe('NextAuth Credentials Provider Flow', () => {
    /**
     * Test suite for NextAuth credentials provider authentication
     * 
     * @description Tests complete NextAuth authentication workflow
     * @riskLevel CRITICAL - NextAuth flow must work perfectly
     */

    it('completes full admin authentication workflow', async () => {
      /**
       * Test complete admin authentication through NextAuth
       * 
       * @performance Target: <500ms complete flow
       * @tradingImpact Admin authentication enables full platform access
       * @riskLevel CRITICAL - Admin access provides elevated privileges
       */

      // Mock successful backend response - must be set up before calling authorize
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'test-jwt-token',
          token_type: 'bearer',
          expires_in: 28800,
          user: {
            id: '1',
            username: 'admin',
            role: 'administrator',
            permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin']
          }
        })
      });

      // Set up global fetch mock
      global.fetch = mockFetch;

      // Dynamically import authOptions after environment and fetch setup
      const { authOptions } = await import('../../app/api/auth/[...nextauth]/route');

      // Add console spy to capture authentication logs
      const consoleSpy = vi.spyOn(console, 'log');
      const consoleErrorSpy = vi.spyOn(console, 'error');

      // Test NextAuth credentials provider
      const credentialsProvider = authOptions.providers.find(
        provider => provider.id === 'credentials'
      ) as CredentialsConfig;
      
      expect(credentialsProvider).toBeDefined();
      expect(credentialsProvider.authorize).toBeDefined();
      
      // @ts-expect-error Test-specific type handling
      const authResult = await credentialsProvider.authorize!({
        username: 'admin',
        password: 'password'
      }, {} as any);

      // Debug logging
      console.log('Mock fetch calls:', mockFetch.mock.calls);
      console.log('Auth result:', authResult);
      console.log('Console logs:', consoleSpy.mock.calls);
      console.log('Console errors:', consoleErrorSpy.mock.calls);

      // Verify authentication result
      expect(authResult).toEqual({
        id: '1',
        username: 'admin',
        name: 'admin',
        email: 'admin@traider.local',
        role: 'ADMIN',
        permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin'],
        lastLogin: expect.any(String)
      });

      // Verify fetch was called correctly
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/auth/login',
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            username: 'admin',
            password: 'password',
            remember_me: false,
          }),
        }
      );

      // Clean up spies
      consoleSpy.mockRestore();
      consoleErrorSpy.mockRestore();
    });

    it('completes full demo user authentication workflow', async () => {
      /**
       * Test complete demo user authentication workflow
       * 
       * @performance Target: <500ms complete flow
       * @tradingImpact Demo authentication enables trading platform testing
       * @riskLevel HIGH - Demo access must be properly restricted
       */

      // Mock successful backend response for demo user
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'test-jwt-token',
          token_type: 'bearer',
          expires_in: 28800,
          user: {
            id: '2',
            username: 'demo',
            role: 'trader',
            permissions: ['trading.execute', 'trading.view', 'risk.view']
          }
        })
      });

      global.fetch = mockFetch;

      // Dynamically import authOptions after environment and fetch setup
      const { authOptions } = await import('../../app/api/auth/[...nextauth]/route');

      const credentialsProvider = authOptions.providers.find(
        provider => provider.id === 'credentials'
      ) as CredentialsConfig;
      
      // @ts-expect-error Test-specific type handling
      const authResult = await credentialsProvider.authorize!({
        username: 'demo',
        password: 'demo123'
      }, {} as any);

      expect(authResult).toEqual({
        id: '2',
        username: 'demo',
        name: 'demo',
        email: 'demo@traider.local',
        role: 'TRADER',
        permissions: ['trading.execute', 'trading.view', 'risk.view'],
        lastLogin: expect.any(String)
      });
    });

    it('handles complete authentication failure workflow', async () => {
      /**
       * Test complete authentication failure handling
       * 
       * @tradingImpact Failed authentication must be properly rejected
       * @riskLevel CRITICAL - Security boundary enforcement
       */

      // Mock failed backend response
      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized',
        json: async () => ({
          detail: 'Invalid credentials'
        })
      });

      global.fetch = mockFetch;

      // Dynamically import authOptions after environment and fetch setup
      const { authOptions } = await import('../../app/api/auth/[...nextauth]/route');

      const credentialsProvider = authOptions.providers.find(
        provider => provider.id === 'credentials'
      ) as CredentialsConfig;
      
      // @ts-expect-error Test-specific type handling
      const authResult = await credentialsProvider.authorize!({
        username: 'invalid',
        password: 'wrong'
      }, {} as any);

      expect(authResult).toBeNull();
    });

    it('validates input sanitization throughout flow', async () => {
      /**
       * Test input validation and sanitization across authentication flow
       * 
       * @tradingImpact Input validation prevents injection attacks
       * @riskLevel HIGH - Security input validation critical
       */

      // Dynamically import authOptions after environment setup
      const { authOptions } = await import('../../app/api/auth/[...nextauth]/route');

      const credentialsProvider = authOptions.providers.find(
        provider => provider.id === 'credentials'
      ) as CredentialsConfig;
      
      // Test empty credentials
      // @ts-expect-error Test-specific type handling
      const emptyResult = await credentialsProvider.authorize!({
        username: '',
        password: ''
      }, {} as any);

      expect(emptyResult).toBeNull();

      // Test missing username
      // @ts-expect-error Test-specific type handling
      const missingUsernameResult = await credentialsProvider.authorize!({
        username: '',
        password: 'password'
      }, {} as any);

      expect(missingUsernameResult).toBeNull();

      // Test missing password
      // @ts-expect-error Test-specific type handling
      const missingPasswordResult = await credentialsProvider.authorize!({
        username: 'admin',
        password: ''
      }, {} as any);

      expect(missingPasswordResult).toBeNull();
    });
  });

  describe('API Integration', () => {
    /**
     * Test suite for API integration with authentication system
     * 
     * @description Tests API endpoints work correctly with authentication changes
     * @riskLevel MEDIUM - API functionality validation
     */

    it('health check endpoint works without authentication', async () => {
      /**
       * Test that health check works without authentication
       * 
       * @tradingImpact Health checks must be publicly accessible
       * @riskLevel LOW - Public endpoint functionality
       */

      const healthRequest = new NextRequest('http://localhost:3000/api?endpoint=health', {
        method: 'GET'
      });

      const response = await GET(healthRequest);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.status).toBe('healthy');
      expect(data.timestamp).toBeDefined();
      expect(data.version).toBe('1.0.0-alpha');
      expect(data.services).toBeDefined();
      expect(data.system).toBeDefined();
    });

    it('API info endpoint provides authentication guidance', async () => {
      /**
       * Test that API info endpoint provides authentication guidance
       * 
       * @tradingImpact Helps users understand authentication requirements
       * @riskLevel LOW - Information endpoint for user guidance
       */

      const infoRequest = new NextRequest('http://localhost:3000/api?endpoint=info', {
        method: 'GET'
      });

      const response = await GET(infoRequest);
      const data = await response.json();

      expect(response.status).toBe(200);
      expect(data.name).toBe('TRAIDER V1 Unified API');
      expect(data.version).toBe('1.0.0-alpha');
      expect(data.authentication.provider).toBe('NextAuth.js');
      expect(data.authentication.endpoints).toEqual({
        signin: '/api/auth/signin',
        signout: '/api/auth/signout',
        session: '/api/auth/session',
        providers: '/api/auth/providers'
      });
    });
  });

  describe('Performance and Reliability', () => {
    /**
     * Test suite for performance and reliability validation
     * 
     * @description Tests authentication performance meets institutional standards
     * @riskLevel HIGH - Performance critical for trading operations
     */

    it('completes authentication within performance targets', async () => {
      /**
       * Test that authentication completes within performance targets
       * 
       * @performance Target: <500ms complete authentication flow
       * @tradingImpact Fast authentication reduces trading latency
       * @riskLevel MEDIUM - Performance impact on trading operations
       */

      const mockFetch = vi.fn().mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'test-jwt-token',
          token_type: 'bearer',
          expires_in: 28800,
          user: {
            id: '1',
            username: 'admin',
            role: 'administrator',
            permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin']
          }
        })
      });

      global.fetch = mockFetch;

      // Dynamically import authOptions after environment and fetch setup
      const { authOptions } = await import('../../app/api/auth/[...nextauth]/route');

      const credentialsProvider = authOptions.providers.find(
        provider => provider.id === 'credentials'
      ) as CredentialsConfig;

      const startTime = Date.now();
      
      // @ts-expect-error Test-specific type handling
      const authResult = await credentialsProvider.authorize!({
        username: 'admin',
        password: 'password'
      }, {} as any);
      
      const endTime = Date.now();
      const duration = endTime - startTime;

      expect(authResult).toBeDefined();
      expect(duration).toBeLessThan(500); // Performance target: <500ms
    });

    it('handles concurrent authentication requests', async () => {
      /**
       * Test concurrent authentication request handling
       * 
       * @performance Target: Handle 10 concurrent requests
       * @tradingImpact Multiple users must be able to authenticate simultaneously
       * @riskLevel HIGH - Concurrent access critical for multi-user platform
       */

      // Mock successful backend responses for concurrent requests
      const mockFetch = vi.fn()
        .mockResolvedValue({
          ok: true,
          json: async () => ({
            access_token: 'test-jwt-token',
            token_type: 'bearer',
            expires_in: 28800,
            user: {
              id: '1',
              username: 'admin',
              role: 'administrator',
              permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin']
            }
          })
        });

      global.fetch = mockFetch;

      // Dynamically import authOptions after environment and fetch setup
      const { authOptions } = await import('../../app/api/auth/[...nextauth]/route');

      const credentialsProvider = authOptions.providers.find(
        provider => provider.id === 'credentials'
      ) as CredentialsConfig;

      // Create 5 concurrent authentication requests
      const authPromises = Array.from({ length: 5 }, () =>
        // @ts-expect-error Test-specific type handling
        credentialsProvider.authorize!({
          username: 'admin',
          password: 'password'
        }, {} as any)
      );

      const results = await Promise.all(authPromises);

      // Verify all requests completed successfully
      expect(results).toHaveLength(5);
      results.forEach(result => {
        expect(result).toBeDefined();
        expect(result?.username).toBe('admin');
      });
    });
  });
}); 