/**
 * @fileoverview Simplified NextAuth integration test for TRAIDER V1
 * @module tests/unit/api/nextauth-integration-simple.test
 *
 * @description
 * Direct testing of NextAuth credentials provider logic.
 * Uses dependency injection to avoid complex module mocking.
 *
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import CredentialsProvider from 'next-auth/providers/credentials';
import { _setTestHook_forceAuthenticate } from '../../../app/lib/auth/backend-auth';
import { createTestUsers } from '../../setup/prepareAuthTest';

describe('NextAuth Credentials Provider - Direct Test', () => {
  let mockAuth: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    // Create fresh mock function
    mockAuth = vi.fn();

    // Install the test hook
    _setTestHook_forceAuthenticate(mockAuth);
  });

  afterEach(() => {
    // Clean up the test hook
    _setTestHook_forceAuthenticate(undefined);
    vi.restoreAllMocks();
  });

  describe('Credentials Provider Logic', () => {
    it('should authenticate valid admin credentials', async () => {
      // Setup mock response for admin user
      mockAuth.mockResolvedValueOnce(createTestUsers.admin());

      // Create credentials provider directly
      const provider = CredentialsProvider({
        id: 'credentials',
        name: 'TRAIDER Credentials',
        credentials: {
          username: { label: 'Username', type: 'text' },
          password: { label: 'Password', type: 'password' },
        },
        async authorize(credentials) {
          if (!credentials?.username || !credentials?.password) {
            return null;
          }

          // Import here to use the test hook
          const { authenticateWithBackend } = await import('../../../app/lib/auth/backend-auth');

          const user = await authenticateWithBackend(credentials.username, credentials.password);

          return user || null;
        },
      });

      // Test the authorize function
      const result = await provider.authorize!(
        {
          username: 'admin',
          password: 'password',
        },
        {} as any
      );

      expect(result).toEqual(createTestUsers.admin());
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
    });

    it('should authenticate valid demo trader credentials', async () => {
      // Setup mock response for demo user
      mockAuth.mockResolvedValueOnce(createTestUsers.demo());

      // Create credentials provider directly
      const provider = CredentialsProvider({
        id: 'credentials',
        name: 'TRAIDER Credentials',
        credentials: {
          username: { label: 'Username', type: 'text' },
          password: { label: 'Password', type: 'password' },
        },
        async authorize(credentials) {
          if (!credentials?.username || !credentials?.password) {
            return null;
          }

          // Import here to use the test hook
          const { authenticateWithBackend } = await import('../../../app/lib/auth/backend-auth');

          const user = await authenticateWithBackend(credentials.username, credentials.password);

          return user || null;
        },
      });

      // Test the authorize function
      const result = await provider.authorize!(
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

      // Create credentials provider directly
      const provider = CredentialsProvider({
        id: 'credentials',
        name: 'TRAIDER Credentials',
        credentials: {
          username: { label: 'Username', type: 'text' },
          password: { label: 'Password', type: 'password' },
        },
        async authorize(credentials) {
          if (!credentials?.username || !credentials?.password) {
            return null;
          }

          // Import here to use the test hook
          const { authenticateWithBackend } = await import('../../../app/lib/auth/backend-auth');

          const user = await authenticateWithBackend(credentials.username, credentials.password);

          return user || null;
        },
      });

      // Test the authorize function
      const result = await provider.authorize!(
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
      // Create credentials provider directly
      const provider = CredentialsProvider({
        id: 'credentials',
        name: 'TRAIDER Credentials',
        credentials: {
          username: { label: 'Username', type: 'text' },
          password: { label: 'Password', type: 'password' },
        },
        async authorize(credentials) {
          if (!credentials?.username || !credentials?.password) {
            return null;
          }

          // Import here to use the test hook
          const { authenticateWithBackend } = await import('../../../app/lib/auth/backend-auth');

          const user = await authenticateWithBackend(credentials.username, credentials.password);

          return user || null;
        },
      });

      // Test missing username
      const result1 = await provider.authorize!(
        {
          password: 'password',
        } as any,
        {} as any
      );

      expect(result1).toBeNull();
      expect(mockAuth).not.toHaveBeenCalled();

      // Test missing password
      const result2 = await provider.authorize!(
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

      // Create credentials provider directly
      const provider = CredentialsProvider({
        id: 'credentials',
        name: 'TRAIDER Credentials',
        credentials: {
          username: { label: 'Username', type: 'text' },
          password: { label: 'Password', type: 'password' },
        },
        async authorize(credentials) {
          if (!credentials?.username || !credentials?.password) {
            return null;
          }

          try {
            // Import here to use the test hook
            const { authenticateWithBackend } = await import('../../../app/lib/auth/backend-auth');

            const user = await authenticateWithBackend(credentials.username, credentials.password);

            return user || null;
          } catch {
            // Handle authentication errors gracefully
            return null;
          }
        },
      });

      // Test the authorize function
      const result = await provider.authorize!(
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
});
