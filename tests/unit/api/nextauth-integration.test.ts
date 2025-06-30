/**
 * @fileoverview NextAuth integration tests for TRAIDER V1
 * @module tests/unit/api/nextauth-integration.test
 * 
 * @description
 * Tests NextAuth.js integration with FastAPI backend authentication.
 * Validates credential provider, session management, and error handling.
 * 
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { NextRequest } from 'next/server';
import { authOptions } from '../../../app/api/auth/[...nextauth]/route';
import type { Session } from 'next-auth';

// Mock fetch for backend API calls
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Mock environment variables
const originalEnv = process.env;

describe('NextAuth Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    process.env = {
      ...originalEnv,
      NEXT_PUBLIC_API_URL: 'http://localhost:8000',
      NEXTAUTH_SECRET: 'test-secret-key-for-testing-only',
    };
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  describe('Credentials Provider', () => {
    it('should authenticate valid admin credentials', async () => {
      // Mock successful backend response
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'mock-token-for-testing',
          token_type: 'bearer',
          expires_in: 28800,
          user: {
            id: '1',
            username: 'admin',
            role: 'administrator',
            permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin'],
          },
        }),
      });

      const credentialsProvider = authOptions.providers[0];
      
      if ('authorize' in credentialsProvider) {
        const result = await credentialsProvider.authorize!(
          {
            username: 'admin',
            password: 'password',
          },
          {} as any
        );

        expect(result).toEqual({
          id: '1',
          username: 'admin',
          name: 'admin',
          email: 'admin@traider.local',
          role: 'ADMIN',
          permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin'],
          lastLogin: expect.any(String),
        });

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
      }
    });

    it('should authenticate valid demo trader credentials', async () => {
      // Mock successful backend response for demo user
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'mock-demo-token',
          token_type: 'bearer',
          expires_in: 28800,
          user: {
            id: '2',
            username: 'demo',
            role: 'trader',
            permissions: ['trading.execute', 'trading.view', 'risk.view'],
          },
        }),
      });

      const credentialsProvider = authOptions.providers[0];
      
      if ('authorize' in credentialsProvider) {
        const result = await credentialsProvider.authorize!(
          {
            username: 'demo',
            password: 'demo123',
          },
          {} as any
        );

        expect(result).toEqual({
          id: '2',
          username: 'demo',
          name: 'demo',
          email: 'demo@traider.local',
          role: 'TRADER',
          permissions: ['trading.execute', 'trading.view', 'risk.view'],
          lastLogin: expect.any(String),
        });
      }
    });

    it('should reject invalid credentials', async () => {
      // Mock failed backend response
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({
          detail: 'Invalid username or password',
        }),
      });

      const credentialsProvider = authOptions.providers[0];
      
      if ('authorize' in credentialsProvider) {
        const result = await credentialsProvider.authorize!(
          {
            username: 'invalid',
            password: 'wrong',
          },
          {} as any
        );

        expect(result).toBeNull();
      }
    });

    it('should handle missing credentials', async () => {
      const credentialsProvider = authOptions.providers[0];
      
      if ('authorize' in credentialsProvider) {
        const result = await credentialsProvider.authorize!(
          {
            username: '',
            password: '',
          },
          {} as any
        );

        expect(result).toBeNull();
        expect(mockFetch).not.toHaveBeenCalled();
      }
    });

    it('should handle backend service errors', async () => {
      // Mock network error
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const credentialsProvider = authOptions.providers[0];
      
      if ('authorize' in credentialsProvider) {
        const result = await credentialsProvider.authorize!(
          {
            username: 'admin',
            password: 'password',
          },
          {} as any
        );

        expect(result).toBeNull();
      }
    });
  });

  describe('JWT Callback', () => {
    it('should persist user data in token on sign in', async () => {
      const user = {
        id: '1',
        username: 'admin',
        name: 'admin',
        email: 'admin@traider.local',
        role: 'ADMIN' as const,
        permissions: ['trading.execute', 'system.admin'],
        lastLogin: '2024-01-01T00:00:00.000Z',
      };

      const token = {};

      const result = await authOptions.callbacks!.jwt!({
        token,
        user,
        account: null,
        profile: undefined,
        isNewUser: false,
      });

      expect(result).toEqual({
        id: '1',
        username: 'admin',
        email: 'admin@traider.local',
        role: 'ADMIN',
        permissions: ['trading.execute', 'system.admin'],
        lastLogin: '2024-01-01T00:00:00.000Z',
      });
    });

    it('should preserve existing token data when user is not provided', async () => {
      const existingToken = {
        id: '1',
        username: 'admin',
        role: 'ADMIN',
        permissions: ['trading.execute'],
      };

      const result = await authOptions.callbacks!.jwt!({
        token: existingToken,
        user: undefined,
        account: null,
        profile: undefined,
        isNewUser: false,
      });

      expect(result).toEqual(existingToken);
    });
  });

  describe('Session Callback', () => {
    it('should transform token data to session format', async () => {
      const session: Session = {
        user: {
          name: 'admin',
          email: 'admin@traider.local',
        },
        expires: '2024-12-31T23:59:59.000Z',
      };

      const token = {
        id: '1',
        username: 'admin',
        email: 'admin@traider.local',
        role: 'ADMIN',
        permissions: ['trading.execute', 'system.admin'],
        lastLogin: '2024-01-01T00:00:00.000Z',
      };

      const result = await authOptions.callbacks!.session!({
        session,
        token,
        user: undefined,
      });

      expect(result.user).toEqual({
        name: 'admin',
        email: 'admin@traider.local',
        id: '1',
        username: 'admin',
        role: 'ADMIN',
        permissions: ['trading.execute', 'system.admin'],
        lastLogin: '2024-01-01T00:00:00.000Z',
      });
    });

    it('should handle missing token data gracefully', async () => {
      const session: Session = {
        user: {
          name: 'user',
          email: 'user@example.com',
        },
        expires: '2024-12-31T23:59:59.000Z',
      };

      const token = {};

      const result = await authOptions.callbacks!.session!({
        session,
        token,
        user: undefined,
      });

      expect(result.user).toEqual({
        name: 'user',
        email: 'user@example.com',
        id: undefined,
        username: undefined,
        role: undefined,
        permissions: undefined,
      });
    });
  });

  describe('Role Mapping', () => {
    const testCases = [
      { backend: 'administrator', expected: 'ADMIN' },
      { backend: 'admin', expected: 'ADMIN' },
      { backend: 'trader', expected: 'TRADER' },
      { backend: 'trading', expected: 'TRADER' },
      { backend: 'viewer', expected: 'VIEWER' },
      { backend: 'view', expected: 'VIEWER' },
      { backend: 'readonly', expected: 'VIEWER' },
      { backend: 'unknown', expected: 'VIEWER' },
      { backend: '', expected: 'VIEWER' },
    ];

    testCases.forEach(({ backend, expected }) => {
      it(`should map "${backend}" role to "${expected}"`, async () => {
        mockFetch.mockResolvedValueOnce({
          ok: true,
          json: async () => ({
            access_token: 'test-token',
            token_type: 'bearer',
            expires_in: 28800,
            user: {
              id: '1',
              username: 'testuser',
              role: backend,
              permissions: [],
            },
          }),
        });

        const credentialsProvider = authOptions.providers[0];
        
        if ('authorize' in credentialsProvider) {
          const result = await credentialsProvider.authorize!(
            {
              username: 'testuser',
              password: 'password',
            },
            {} as any
          );

          expect(result?.role).toBe(expected);
        }
      });
    });
  });

  describe('Configuration', () => {
    it('should have correct session strategy', () => {
      expect(authOptions.session?.strategy).toBe('jwt');
    });

    it('should have correct session timeouts', () => {
      expect(authOptions.session?.maxAge).toBe(8 * 60 * 60); // 8 hours
      expect(authOptions.session?.updateAge).toBe(60 * 60);   // 1 hour
    });

    it('should have correct JWT timeout', () => {
      expect(authOptions.jwt?.maxAge).toBe(8 * 60 * 60); // 8 hours
    });

    it('should have correct pages configuration', () => {
      expect(authOptions.pages?.signIn).toBe('/login');
      expect(authOptions.pages?.error).toBe('/login');
    });

    it('should enable debug in development', () => {
      process.env.NODE_ENV = 'development';
      expect(authOptions.debug).toBe(true);
    });
  });
}); 