/**
 * @fileoverview Working NextAuth integration test for TRAIDER V1
 * @module tests/unit/api/nextauth-working.test
 *
 * @description
 * Comprehensive NextAuth authentication testing using dependency injection.
 * Tests the actual NextAuth route configuration with mocked backend.
 *
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { _setTestHook_forceAuthenticate } from '../../../app/lib/auth/backend-auth';
import { createTestUsers } from '../../setup/prepareAuthTest';

describe('NextAuth Integration - Working Tests', () => {
  let mockAuth: ReturnType<typeof vi.fn>;
  let authOptions: any;

  beforeEach(async () => {
    // Create fresh mock function
    mockAuth = vi.fn();

    // Install the test hook BEFORE importing the route
    _setTestHook_forceAuthenticate(mockAuth);

    // Set environment variables
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
    process.env.NEXTAUTH_SECRET = 'test-secret-key-for-testing-only';

    // Import authOptions after the test hook is installed
    const authModule = await import('../../../app/api/auth/[...nextauth]/route');
    authOptions = authModule.authOptions;
  });

  afterEach(() => {
    // Clean up the test hook
    _setTestHook_forceAuthenticate(undefined);
    vi.restoreAllMocks();
  });

  describe('Credentials Provider Authentication', () => {
    it('should authenticate valid admin credentials', async () => {
      // Setup mock response for admin user
      mockAuth.mockResolvedValueOnce(createTestUsers.admin());

      // Get the credentials provider from authOptions
      const credentialsProvider = authOptions.providers.find(
        (provider: any) => provider.id === 'credentials'
      );

      expect(credentialsProvider).toBeDefined();
      expect(credentialsProvider.authorize).toBeDefined();

      // Test the authorize function
      const result = await credentialsProvider.authorize(
        {
          username: 'admin',
          password: 'password',
        },
        {} as any
      );

      // Verify authentication result
      expect(result).toEqual(createTestUsers.admin());
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
    });

    it('should authenticate valid demo trader credentials', async () => {
      // Setup mock response for demo user
      mockAuth.mockResolvedValueOnce(createTestUsers.demo());

      const credentialsProvider = authOptions.providers.find(
        (provider: any) => provider.id === 'credentials'
      );

      const result = await credentialsProvider.authorize(
        {
          username: 'demo',
          password: 'demo123',
        },
        {} as any
      );

      expect(result).toEqual(createTestUsers.demo());
      expect(mockAuth).toHaveBeenCalledWith('demo', 'demo123');
    });

    it('should reject invalid credentials', async () => {
      // Setup mock response for invalid credentials
      mockAuth.mockResolvedValueOnce(null);

      const credentialsProvider = authOptions.providers.find(
        (provider: any) => provider.id === 'credentials'
      );

      const result = await credentialsProvider.authorize(
        {
          username: 'invalid',
          password: 'wrong',
        },
        {} as any
      );

      expect(result).toBeNull();
      expect(mockAuth).toHaveBeenCalledWith('invalid', 'wrong');
    });

    it('should handle missing credentials', async () => {
      const credentialsProvider = authOptions.providers.find(
        (provider: any) => provider.id === 'credentials'
      );

      // Test missing username
      const result1 = await credentialsProvider.authorize(
        {
          password: 'password',
        } as any,
        {} as any
      );

      expect(result1).toBeNull();
      expect(mockAuth).not.toHaveBeenCalled();

      // Test missing password
      const result2 = await credentialsProvider.authorize(
        {
          username: 'admin',
        } as any,
        {} as any
      );

      expect(result2).toBeNull();
      expect(mockAuth).not.toHaveBeenCalled();
    });

    it('should handle backend service errors', async () => {
      // Setup mock to throw error
      mockAuth.mockRejectedValueOnce(new Error('Backend service unavailable'));

      const credentialsProvider = authOptions.providers.find(
        (provider: any) => provider.id === 'credentials'
      );

      const result = await credentialsProvider.authorize(
        {
          username: 'admin',
          password: 'password',
        },
        {} as any
      );

      expect(result).toBeNull();
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
    });
  });

  describe('JWT and Session Callbacks', () => {
    it('should persist user data in JWT token', async () => {
      const testUser = createTestUsers.admin();

      const jwtResult = await authOptions.callbacks.jwt({
        token: {},
        user: testUser,
      });

      expect(jwtResult.id).toBe('1');
      expect(jwtResult.username).toBe('admin');
      expect(jwtResult.email).toBe('admin@traider.local');
      expect(jwtResult.role).toBe('ADMIN');
      expect(jwtResult.permissions).toEqual([
        'trading.execute',
        'trading.view',
        'risk.manage',
        'system.admin',
      ]);
      expect(jwtResult.lastLogin).toBe('2024-01-01T00:00:00.000Z');
    });

    it('should transform JWT token to session format', async () => {
      const token = {
        id: '1',
        username: 'admin',
        email: 'admin@traider.local',
        role: 'ADMIN',
        permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin'],
        lastLogin: '2024-01-01T00:00:00.000Z',
      };

      const sessionResult = await authOptions.callbacks.session({
        session: { user: {} },
        token,
      });

      expect(sessionResult.user.id).toBe('1');
      expect(sessionResult.user.username).toBe('admin');
      expect(sessionResult.user.role).toBe('ADMIN');
      expect(sessionResult.user.permissions).toEqual([
        'trading.execute',
        'trading.view',
        'risk.manage',
        'system.admin',
      ]);
      expect(sessionResult.user.lastLogin).toBe('2024-01-01T00:00:00.000Z');
    });
  });

  describe('Configuration Validation', () => {
    it('should have correct session configuration', () => {
      expect(authOptions.session.strategy).toBe('jwt');
      expect(authOptions.session.maxAge).toBe(8 * 60 * 60); // 8 hours
      expect(authOptions.session.updateAge).toBe(60 * 60); // 1 hour
    });

    it('should have correct JWT configuration', () => {
      expect(authOptions.jwt.maxAge).toBe(8 * 60 * 60); // 8 hours
    });

    it('should have correct page configuration', () => {
      expect(authOptions.pages.signIn).toBe('/login');
      expect(authOptions.pages.error).toBe('/login');
    });

    it('should have correct provider configuration', () => {
      expect(authOptions.providers).toBeDefined();
      expect(authOptions.providers.length).toBe(1);

      const credentialsProvider = authOptions.providers[0];
      expect(credentialsProvider.id).toBe('credentials');
      expect(credentialsProvider.name).toBe('TRAIDER Credentials');
    });
  });
});
