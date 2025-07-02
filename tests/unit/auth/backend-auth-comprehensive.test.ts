/**
 * @fileoverview Comprehensive tests for backend authentication service
 * @module tests/unit/auth/backend-auth-comprehensive
 *
 * @description
 * Comprehensive test suite for the backend authentication service including
 * role mapping, authentication flow, error handling, and test hooks.
 *
 * @performance
 * - Test execution: <100ms per test
 * - Memory usage: <10MB
 *
 * @risk
 * - Failure impact: CRITICAL - Authentication gateway testing
 * - Recovery strategy: Validate all auth paths
 *
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { createStandardTestSuite } from '../../utils/sharedTestUtilities';
import {
  authenticateWithBackend,
  mapBackendRole,
  _setTestHook_forceAuthenticate,
} from '../../../app/lib/auth/backend-auth';

describe('🔐 Backend Authentication Service', () => {
  const testSuite = createStandardTestSuite({ setupRouter: false });

  beforeEach(() => {
    testSuite.beforeEach();
    // Reset test hooks after standard setup
    _setTestHook_forceAuthenticate(undefined);
  });

  afterEach(() => {
    testSuite.afterEach();
    // Clean up test hooks
    _setTestHook_forceAuthenticate(undefined);
  });

  describe('Role Mapping', () => {
    it('should map admin roles correctly', () => {
      expect(mapBackendRole('admin')).toBe('ADMIN');
      expect(mapBackendRole('administrator')).toBe('ADMIN');
      expect(mapBackendRole('ADMIN')).toBe('ADMIN');
      expect(mapBackendRole('Administrator')).toBe('ADMIN');
    });

    it('should map trader roles correctly', () => {
      expect(mapBackendRole('trader')).toBe('TRADER');
      expect(mapBackendRole('trading')).toBe('TRADER');
      expect(mapBackendRole('TRADER')).toBe('TRADER');
      expect(mapBackendRole('Trading')).toBe('TRADER');
    });

    it('should map viewer roles correctly', () => {
      expect(mapBackendRole('viewer')).toBe('VIEWER');
      expect(mapBackendRole('view')).toBe('VIEWER');
      expect(mapBackendRole('readonly')).toBe('VIEWER');
      expect(mapBackendRole('VIEWER')).toBe('VIEWER');
      expect(mapBackendRole('ReadOnly')).toBe('VIEWER');
    });

    it('should default to VIEWER for unknown roles', () => {
      expect(mapBackendRole('unknown')).toBe('VIEWER');
      expect(mapBackendRole('invalid')).toBe('VIEWER');
      expect(mapBackendRole('')).toBe('VIEWER');
      expect(mapBackendRole('123')).toBe('VIEWER');
      expect(mapBackendRole('null')).toBe('VIEWER');
    });

    it('should handle edge cases in role mapping', () => {
      expect(mapBackendRole('admin ')).toBe('VIEWER'); // Trailing space
      expect(mapBackendRole(' admin')).toBe('VIEWER'); // Leading space
      expect(mapBackendRole('admin\n')).toBe('VIEWER'); // Newline
      expect(mapBackendRole('admin\t')).toBe('VIEWER'); // Tab
    });

    it('should be case insensitive for valid roles', () => {
      expect(mapBackendRole('AdMiN')).toBe('ADMIN');
      expect(mapBackendRole('TrAdEr')).toBe('TRADER');
      expect(mapBackendRole('ViEwEr')).toBe('VIEWER');
    });
  });

  describe('Authentication Flow', () => {
    it('should authenticate successfully with valid credentials', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            username: 'admin',
            role: 'admin',
            permissions: ['READ', 'WRITE', 'ADMIN'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('admin', 'password', mockFetch);

      expect(mockFetch).toHaveBeenCalledWith('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: 'admin',
          password: 'password',
          remember_me: false,
        }),
      });

      expect(result).toEqual({
        id: 'user-123',
        username: 'admin',
        name: 'admin',
        email: 'admin@traider.local',
        role: 'ADMIN',
        permissions: ['READ', 'WRITE', 'ADMIN'],
        lastLogin: expect.any(String),
      });
    });

    it('should return null for invalid credentials', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: vi.fn().mockResolvedValue({ error: 'Invalid credentials' }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('invalid', 'credentials', mockFetch);

      expect(result).toBeNull();
      expect(mockResponse.json).toHaveBeenCalled();
    });

    it('should handle network errors gracefully', async () => {
      const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'));

      const result = await authenticateWithBackend('admin', 'password', mockFetch);

      expect(result).toBeNull();
    });

    it('should handle successful response with invalid JSON', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON')),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('admin', 'password', mockFetch);

      expect(result).toBeNull();
    });

    it('should use custom API URL from environment', async () => {
      const originalApiUrl = process.env.NEXT_PUBLIC_API_URL;
      process.env.NEXT_PUBLIC_API_URL = 'https://api.traider.com';

      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            username: 'admin',
            role: 'admin',
            permissions: ['READ', 'WRITE'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      await authenticateWithBackend('admin', 'password', mockFetch);

      expect(mockFetch).toHaveBeenCalledWith(
        'https://api.traider.com/auth/login',
        expect.any(Object)
      );

      // Restore original environment
      if (originalApiUrl !== undefined) {
        process.env.NEXT_PUBLIC_API_URL = originalApiUrl;
      } else {
        delete process.env.NEXT_PUBLIC_API_URL;
      }
    });
  });

  describe('Test Hook System', () => {
    it('should use test hook when available', async () => {
      const mockUser = {
        id: 'test-user',
        username: 'testuser',
        name: 'Test User',
        email: 'test@traider.local',
        role: 'ADMIN' as const,
        permissions: ['READ', 'WRITE'],
        lastLogin: '2024-01-01T00:00:00Z',
      };

      const mockHook = vi.fn().mockResolvedValue(mockUser);
      _setTestHook_forceAuthenticate(mockHook);

      const result = await authenticateWithBackend('testuser', 'password');

      expect(mockHook).toHaveBeenCalledWith('testuser', 'password');
      expect(result).toEqual(mockUser);
    });

    it('should handle test hook errors gracefully', async () => {
      const mockHook = vi.fn().mockRejectedValue(new Error('Test error'));
      _setTestHook_forceAuthenticate(mockHook);

      const result = await authenticateWithBackend('testuser', 'password');

      expect(mockHook).toHaveBeenCalledWith('testuser', 'password');
      expect(result).toBeNull();
    });
  });

  describe('Error Handling', () => {
    it('should handle malformed JSON response', async () => {
      const mockResponse = {
        ok: false,
        status: 401,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON')),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('invalid', 'credentials', mockFetch);

      expect(result).toBeNull();
    });

    it('should handle successful response with invalid JSON', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockRejectedValue(new Error('Invalid JSON')),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('admin', 'password', mockFetch);

      expect(result).toBeNull();
    });
  });

  describe('Performance', () => {
    it('should complete authentication within performance targets', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            username: 'admin',
            role: 'admin',
            permissions: ['READ', 'WRITE'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const startTime = performance.now();
      await authenticateWithBackend('admin', 'password', mockFetch);
      const endTime = performance.now();

      // Should complete quickly (excluding network time)
      expect(endTime - startTime).toBeLessThan(50);
    });

    it('should handle concurrent authentication requests', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            username: 'admin',
            role: 'admin',
            permissions: ['READ', 'WRITE'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      // Run multiple concurrent authentications
      const promises = Array.from({ length: 10 }, (_, i) =>
        authenticateWithBackend(`user${i}`, 'password', mockFetch)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      expect(mockFetch).toHaveBeenCalledTimes(10);
      expect(results.every((result) => result !== null)).toBe(true);
    });
  });

  describe('Response Transformation', () => {
    it('should transform backend response to NextAuth user format', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'trader-456',
            username: 'trader1',
            role: 'trader',
            permissions: ['READ', 'TRADE'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('trader1', 'password', mockFetch);

      expect(result).toMatchObject({
        id: 'trader-456',
        username: 'trader1',
        name: 'trader1',
        email: 'trader1@traider.local',
        role: 'TRADER',
        permissions: ['READ', 'TRADE'],
      });

      expect(result?.lastLogin).toMatch(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/);
    });

    it('should handle different role formats in response', async () => {
      const testCases = [
        { backendRole: 'administrator', expectedRole: 'ADMIN' },
        { backendRole: 'trading', expectedRole: 'TRADER' },
        { backendRole: 'readonly', expectedRole: 'VIEWER' },
        { backendRole: 'unknown', expectedRole: 'VIEWER' },
      ];

      for (const testCase of testCases) {
        const mockResponse = {
          ok: true,
          json: vi.fn().mockResolvedValue({
            access_token: 'jwt-token',
            token_type: 'bearer',
            expires_in: 3600,
            user: {
              id: 'user-123',
              username: 'testuser',
              role: testCase.backendRole,
              permissions: ['READ'],
            },
          }),
        };

        const mockFetch = vi.fn().mockResolvedValue(mockResponse);

        const result = await authenticateWithBackend('testuser', 'password', mockFetch);

        expect(result?.role).toBe(testCase.expectedRole);
      }
    });

    it('should generate proper email format', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            username: 'special.user_123',
            role: 'viewer',
            permissions: ['READ'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('special.user_123', 'password', mockFetch);

      expect(result?.email).toBe('special.user_123@traider.local');
    });
  });

  describe('Error Handling Edge Cases', () => {
    it('should handle fetch timeout', async () => {
      const mockFetch = vi.fn().mockImplementation(
        () =>
          new Promise(() => {
            // Never resolves, simulates a hanging request
          })
      );

      const authPromise = authenticateWithBackend('admin', 'password', mockFetch);

      // Advance timers to trigger the 5s timeout in authenticateWithBackend
      await vi.advanceTimersByTimeAsync(5001);

      const result = await authPromise;

      expect(result).toBeNull();
    }, 10000);

    it('should handle response with missing user data', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          // Missing user field
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('admin', 'password', mockFetch);

      expect(result).toBeNull();
    });

    it('should handle response with partial user data', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            // Missing username, role, permissions
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const result = await authenticateWithBackend('admin', 'password', mockFetch);

      expect(result).toBeNull();
    });

    it('should handle empty credentials', async () => {
      const mockFetch = vi.fn();

      const result1 = await authenticateWithBackend('', 'password', mockFetch);
      const result2 = await authenticateWithBackend('username', '', mockFetch);
      const result3 = await authenticateWithBackend('', '', mockFetch);

      // Should still make the request - backend will handle validation
      expect(mockFetch).toHaveBeenCalledTimes(3);
      expect(result1).toBeNull();
      expect(result2).toBeNull();
      expect(result3).toBeNull();
    });
  });

  describe('Security Considerations', () => {
    it('should not expose credentials in fetch calls', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: false,
        json: vi.fn().mockResolvedValue({}),
      });

      await authenticateWithBackend('sensitive-user', 'secret-password', mockFetch);

      expect(mockFetch).toHaveBeenCalledTimes(1);
      // Verify credentials are not in URL (basic security check)
      expect(mockFetch).toHaveBeenCalledWith(
        expect.not.stringContaining('sensitive-user'),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining('sensitive-user'),
        })
      );
    });

    it('should handle credentials with special characters', async () => {
      const mockResponse = {
        ok: true,
        json: vi.fn().mockResolvedValue({
          access_token: 'jwt-token',
          token_type: 'bearer',
          expires_in: 3600,
          user: {
            id: 'user-123',
            username: 'user@domain.com',
            role: 'admin',
            permissions: ['READ'],
          },
        }),
      };

      const mockFetch = vi.fn().mockResolvedValue(mockResponse);

      const specialUsername = 'user@domain.com';
      const specialPassword = 'p@ssw0rd!#$%';

      const result = await authenticateWithBackend(specialUsername, specialPassword, mockFetch);

      expect(result).not.toBeNull();
      expect(result?.username).toBe(specialUsername);

      // Verify special characters are handled correctly in request
      expect(mockFetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          method: 'POST',
          body: expect.stringContaining(specialUsername),
        })
      );
    });
  });
});
