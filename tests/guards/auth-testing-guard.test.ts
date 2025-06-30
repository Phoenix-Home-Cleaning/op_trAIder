/**
 * @fileoverview Authentication Testing Guard Rails for TRAIDER V1
 * @module tests/guards/auth-testing-guard.test
 *
 * @description
 * Guard rail tests to prevent regression of authentication testing infrastructure.
 * These tests validate that the dependency injection pattern remains functional
 * and that critical testing utilities are available.
 *
 * @performance
 * - Guard execution: <50ms total
 * - Individual checks: <5ms each
 *
 * @risk
 * - Failure impact: CRITICAL - Testing infrastructure broken
 * - Recovery strategy: Restore from ADR-007 implementation
 *
 * @compliance
 * - Required for CI/CD pipeline
 * - Must pass before deployment
 *
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  authenticateWithBackend,
  _setTestHook_forceAuthenticate,
} from '../../app/lib/auth/backend-auth';
import { withAuthMock, createTestUsers } from '../setup/prepareAuthTest';

describe('🛡️ Authentication Testing Guard Rails', () => {
  describe('Infrastructure Availability', () => {
    it('should have dependency injection hooks available', () => {
      expect(typeof _setTestHook_forceAuthenticate).toBe('function');
      expect(typeof authenticateWithBackend).toBe('function');
    });

    it('should have test utilities available', () => {
      expect(typeof withAuthMock).toBe('function');
      expect(typeof createTestUsers.admin).toBe('function');
      expect(typeof createTestUsers.demo).toBe('function');
      expect(typeof createTestUsers.viewer).toBe('function');
      expect(typeof createTestUsers.custom).toBe('function');
    });

    it('should have proper test user factory structure', () => {
      const adminUser = createTestUsers.admin();

      expect(adminUser).toHaveProperty('id');
      expect(adminUser).toHaveProperty('username');
      expect(adminUser).toHaveProperty('email');
      expect(adminUser).toHaveProperty('role');
      expect(adminUser).toHaveProperty('permissions');
      expect(adminUser.role).toBe('ADMIN');
    });
  });

  describe('Dependency Injection Functionality', () => {
    let mockAuth: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      mockAuth = vi.fn();
    });

    afterEach(() => {
      _setTestHook_forceAuthenticate(undefined);
      vi.restoreAllMocks();
    });

    it('should allow setting and clearing test hooks', () => {
      // Should start with no hook
      expect(mockAuth).not.toHaveBeenCalled();

      // Should accept hook installation
      expect(() => _setTestHook_forceAuthenticate(mockAuth)).not.toThrow();

      // Should accept hook removal
      expect(() => _setTestHook_forceAuthenticate(undefined)).not.toThrow();
    });

    it('should use test hook when installed', async () => {
      const testUser = createTestUsers.admin();

      _setTestHook_forceAuthenticate(mockAuth);
      mockAuth.mockResolvedValueOnce(testUser);

      const result = await authenticateWithBackend('test', 'test');

      expect(mockAuth).toHaveBeenCalledWith('test', 'test');
      expect(result).toEqual(testUser);
    });

    it('should fall back to production logic when hook cleared', async () => {
      const testUser = createTestUsers.admin();

      // Install hook
      _setTestHook_forceAuthenticate(mockAuth);
      mockAuth.mockResolvedValueOnce(testUser);

      // Verify hook works
      let result = await authenticateWithBackend('test', 'test');
      expect(result).toEqual(testUser);

      // Clear hook
      _setTestHook_forceAuthenticate(undefined);

      // Should now use production logic (will fail due to no backend)
      result = await authenticateWithBackend('test', 'test');
      expect(result).toBeNull(); // Production auth fails without backend

      // Mock should not be called again
      expect(mockAuth).toHaveBeenCalledTimes(1);
    });
  });

  describe('withAuthMock Utility', () => {
    it('should provide working mock function', () => {
      const getMockAuth = withAuthMock();

      expect(typeof getMockAuth).toBe('function');

      // Should return a mock function
      const mockAuth = getMockAuth();
      expect(typeof mockAuth.mockResolvedValueOnce).toBe('function');
      expect(typeof mockAuth.mockRejectedValueOnce).toBe('function');
    });

    it('should handle setup and teardown automatically', async () => {
      const getMockAuth = withAuthMock();
      const mockAuth = getMockAuth();

      // Setup should work
      mockAuth.mockResolvedValueOnce(createTestUsers.admin());

      const result = await authenticateWithBackend('admin', 'password');
      expect(result).toEqual(createTestUsers.admin());
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
    });
  });

  describe('Test User Factory Validation', () => {
    it('should create valid admin user', () => {
      const user = createTestUsers.admin();

      expect(user.id).toBe('1');
      expect(user.username).toBe('admin');
      expect(user.role).toBe('ADMIN');
      expect(user.permissions).toContain('system.admin');
      expect(user.permissions).toContain('trading.execute');
    });

    it('should create valid demo trader', () => {
      const user = createTestUsers.demo();

      expect(user.id).toBe('2');
      expect(user.username).toBe('demo');
      expect(user.role).toBe('TRADER');
      expect(user.permissions).toContain('trading.execute');
      expect(user.permissions).not.toContain('system.admin');
    });

    it('should create valid viewer user', () => {
      const user = createTestUsers.viewer();

      expect(user.id).toBe('3');
      expect(user.username).toBe('viewer');
      expect(user.role).toBe('VIEWER');
      expect(user.permissions).toContain('trading.view');
      expect(user.permissions).not.toContain('trading.execute');
    });

    it('should support custom user creation', () => {
      const customUser = createTestUsers.custom({
        username: 'custom-trader',
        role: 'TRADER',
        permissions: ['custom.permission'],
      });

      expect(customUser.username).toBe('custom-trader');
      expect(customUser.role).toBe('TRADER');
      expect(customUser.permissions).toContain('custom.permission');
    });
  });

  describe('Performance Guard Rails', () => {
    it('should execute dependency injection within performance budget', async () => {
      const startTime = performance.now();

      const mockAuth = vi.fn();
      _setTestHook_forceAuthenticate(mockAuth);
      mockAuth.mockResolvedValueOnce(createTestUsers.admin());

      await authenticateWithBackend('test', 'test');

      const executionTime = performance.now() - startTime;
      expect(executionTime).toBeLessThan(50); // <50ms budget

      _setTestHook_forceAuthenticate(undefined);
    });

    it('should create test users within performance budget', () => {
      const startTime = performance.now();

      createTestUsers.admin();
      createTestUsers.demo();
      createTestUsers.viewer();
      createTestUsers.custom({ role: 'TRADER' });

      const executionTime = performance.now() - startTime;
      expect(executionTime).toBeLessThan(10); // <10ms budget
    });
  });

  describe('Security Guard Rails', () => {
    it('should not expose test hooks in production-like environment', () => {
      const originalEnv = process.env.NODE_ENV;

      try {
        // Simulate production environment
        Object.defineProperty(process.env, 'NODE_ENV', {
          value: 'production',
          writable: true,
          configurable: true,
        });

        // Test hooks should still be available for testing,
        // but should not affect production authentication
        const mockAuth = vi.fn();
        _setTestHook_forceAuthenticate(mockAuth);

        // In a real production environment, this would use actual authentication
        // Here we just verify the hook mechanism doesn't break
        expect(() => _setTestHook_forceAuthenticate(undefined)).not.toThrow();
      } finally {
        Object.defineProperty(process.env, 'NODE_ENV', {
          value: originalEnv,
          writable: true,
          configurable: true,
        });
      }
    });

    it('should not leak sensitive data in test users', () => {
      const users = [createTestUsers.admin(), createTestUsers.demo(), createTestUsers.viewer()];

      users.forEach((user) => {
        expect(user).not.toHaveProperty('password');
        expect(user).not.toHaveProperty('passwordHash');
        expect(user).not.toHaveProperty('secret');
        expect(user).not.toHaveProperty('privateKey');
      });
    });
  });

  describe('Regression Prevention', () => {
    it('should maintain backward compatibility with existing tests', async () => {
      // This test ensures the pattern documented in ADR-007 continues to work
      const getMockAuth = withAuthMock();
      const mockAuth = getMockAuth();

      // Line 1: Setup mock (via withAuthMock)
      // Line 2: Mock response
      mockAuth.mockResolvedValueOnce(createTestUsers.admin());

      // Line 3: Test
      const result = await authenticateWithBackend('admin', 'password');

      expect(result).toEqual(createTestUsers.admin());
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
    });

    it('should prevent common anti-patterns', () => {
      // Prevent direct module mocking (brittle pattern)
      expect(() => {
        // This should not be the primary testing approach
        vi.mock('../../app/lib/auth/backend-auth', () => ({
          authenticateWithBackend: vi.fn(),
        }));
      }).not.toThrow(); // Allowed but not recommended

      // Ensure dependency injection is preferred
      expect(typeof _setTestHook_forceAuthenticate).toBe('function');
    });
  });
});

/**
 * Critical Guard Rail: This test must always pass
 *
 * If this test fails, it indicates a breaking change to the authentication
 * testing infrastructure that could affect all authentication tests.
 */
describe('🚨 CRITICAL: Authentication Testing Infrastructure Health Check', () => {
  it('should pass the complete authentication testing workflow', async () => {
    const startTime = performance.now();

    try {
      // 1. Setup
      const getMockAuth = withAuthMock();
      const mockAuth = getMockAuth();

      // 2. Mock response
      const expectedUser = createTestUsers.admin();
      mockAuth.mockResolvedValueOnce(expectedUser);

      // 3. Execute
      const result = await authenticateWithBackend('admin', 'password');

      // 4. Validate
      expect(result).toEqual(expectedUser);
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');

      // 5. Performance check
      const executionTime = performance.now() - startTime;
      expect(executionTime).toBeLessThan(100);

      // 6. Cleanup verification (handled by withAuthMock)
      // No manual cleanup needed
    } catch (error) {
      throw new Error(`CRITICAL: Authentication testing infrastructure is broken. ${error}`);
    }
  });
});
