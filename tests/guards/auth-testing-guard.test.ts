/**
 * @fileoverview Authentication Testing Guard Rails for TRAIDER V1
 * @module tests/guards/auth-testing-guard.test
 * 
 * @description
 * Comprehensive guard rails to prevent regression of authentication testing
 * infrastructure. Validates environment configuration, dependency injection
 * patterns, and ensures production-mirrored test setup remains functional.
 * 
 * @performance
 * - Guard rail execution: <100ms total
 * - Environment validation: <10ms
 * - Infrastructure checks: <50ms
 * 
 * @risk
 * - Failure impact: CRITICAL - Prevents broken authentication testing
 * - Recovery strategy: Immediate alert and rollback of breaking changes
 * 
 * @compliance
 * - Test infrastructure integrity: 100%
 * - Environment configuration validation: 100%
 * 
 * @see ADR-007: Authentication Testing Strategy
 * @see env.example - Production environment template
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { 
  authTestEnv, 
  createAuthTestUsers, 
  authTestScenarios,
  authTestAssertions,
  TEST_ENVIRONMENT_CONFIG 
} from '../setup/authTestEnvironment';
import { 
  authenticateWithBackend, 
  _setTestHook_forceAuthenticate 
} from '../../app/lib/auth/backend-auth';
// User type imported via authTestEnvironment

describe('🛡️ Authentication Testing Guard Rails', () => {
  describe('Environment Configuration Validation', () => {
    it('should validate all required environment variables match env.example structure', () => {
      // Validate that our test environment mirrors production structure
      const requiredEnvVars = [
        // Frontend Configuration
        'NEXT_PUBLIC_API_URL',
        'NEXTAUTH_URL', 
        'NEXTAUTH_SECRET',
        
        // Backend Configuration
        'DATABASE_URL',
        'SECRET_KEY',
        'ACCESS_TOKEN_EXPIRE_MINUTES',
        'DASHBOARD_PASSWORD',
        'GUEST_PASSWORD',
        
        // Trading & Market Data
        'COINBASE_SANDBOX',
        'MAX_POSITION_SIZE',
        'DAILY_LOSS_LIMIT',
        'EMERGENCY_STOP_ENABLED',
        
        // Database & Infrastructure
        'POSTGRES_USER',
        'POSTGRES_PASSWORD',
        'POSTGRES_DB',
        'POSTGRES_HOST',
        'POSTGRES_PORT',
        'TIMESCALEDB_ENABLED',
        'REDIS_URL',
        
        // Monitoring & Observability
        'LOG_LEVEL',
        'AUDIT_LOG_ENABLED',
        'PROMETHEUS_PORT',
        'GRAFANA_PORT',
        
        // Testing
        'TEST_DATABASE_URL',
        'TEST_SECRET_KEY',
        
        // Security
        'CORS_ORIGINS',
        'CORS_CREDENTIALS',
        'RATE_LIMIT_ENABLED',
        
        // Docker & Infrastructure
        'COMPOSE_PROJECT_NAME',
        'DOCKER_REGISTRY'
      ];

      // Validate all required variables are defined in test config
      requiredEnvVars.forEach(varName => {
        expect(TEST_ENVIRONMENT_CONFIG).toHaveProperty(varName);
        expect(TEST_ENVIRONMENT_CONFIG[varName as keyof typeof TEST_ENVIRONMENT_CONFIG]).toBeDefined();
      });

      // Validate test-safe values
      expect(TEST_ENVIRONMENT_CONFIG.COINBASE_SANDBOX).toBe('true');
      expect(TEST_ENVIRONMENT_CONFIG.NODE_ENV).toBe('test');
      expect(TEST_ENVIRONMENT_CONFIG.RATE_LIMIT_ENABLED).toBe('false');
      expect(TEST_ENVIRONMENT_CONFIG.AUDIT_LOG_ENABLED).toBe('false');
    });

    it('should validate environment isolation setup/teardown', () => {
      const originalEnv = process.env.NEXT_PUBLIC_API_URL;
      
      // Setup should change environment
      authTestEnv.setup();
      expect(process.env.NEXT_PUBLIC_API_URL).toBe(TEST_ENVIRONMENT_CONFIG.NEXT_PUBLIC_API_URL);
      
      // Teardown should restore environment
      authTestEnv.teardown();
      expect(process.env.NEXT_PUBLIC_API_URL).toBe(originalEnv);
    });

    it('should validate test environment security isolation', () => {
      authTestEnv.setup();
      
      // Ensure test secrets are different from production patterns
      expect(process.env.NEXTAUTH_SECRET).toContain('test-');
      expect(process.env.SECRET_KEY).toContain('test-');
      expect(process.env.TEST_SECRET_KEY).toContain('test-');
      
      // Ensure database is isolated
      expect(process.env.DATABASE_URL).toContain('traider_test');
      expect(process.env.POSTGRES_DB).toBe('traider_test');
      
      authTestEnv.teardown();
    });
  });

  describe('Dependency Injection Infrastructure', () => {
    let mockAuth: ReturnType<typeof vi.fn>;

    beforeEach(() => {
      mockAuth = vi.fn();
      authTestEnv.setup();
    });

    afterEach(() => {
      _setTestHook_forceAuthenticate(undefined);
      authTestEnv.teardown();
      vi.restoreAllMocks();
    });

    it('should validate test hook installation and cleanup', async () => {
      // Hook should not be set initially
      expect(mockAuth).not.toHaveBeenCalled();
      
      // Install hook
      _setTestHook_forceAuthenticate(mockAuth);
      mockAuth.mockResolvedValueOnce(createAuthTestUsers.admin());
      
      // Hook should be called when authenticating
      const result = await authenticateWithBackend('admin', 'password');
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
      expect(result).toEqual(createAuthTestUsers.admin());
      
      // Cleanup should remove hook
      _setTestHook_forceAuthenticate(undefined);
      mockAuth.mockClear();
      
      // Hook should not be called after cleanup
      // (This would normally call the real backend, but we're in test mode)
      const _result2 = await authenticateWithBackend('admin', 'password');
      expect(mockAuth).not.toHaveBeenCalled();
    });

    it('should validate error handling in test hooks', async () => {
      // Install hook that throws error
      const errorHook = vi.fn().mockRejectedValue(new Error('Test error'));
      _setTestHook_forceAuthenticate(errorHook);
      
      // Should handle error gracefully and return null
      const result = await authenticateWithBackend('admin', 'password');
      expect(result).toBeNull();
      expect(errorHook).toHaveBeenCalledWith('admin', 'password');
    });

    it('should validate production code path isolation', async () => {
      // Without test hook, should not affect production code
      const result = await authenticateWithBackend('admin', 'password');
      
      // In test environment, this should return null (no real backend)
      // This validates that test hooks don't interfere with production logic
      expect(result).toBeNull();
    });
  });

  describe('Test User Factory Validation', () => {
    it('should validate admin user structure', () => {
      const admin = createAuthTestUsers.admin();
      
      expect(admin.id).toBe('1');
      expect(admin.username).toBe('admin');
      expect(admin.role).toBe('ADMIN');
      expect(admin.permissions).toContain('trading.execute');
      expect(admin.permissions).toContain('system.admin');
      expect(admin.email).toBe('admin@traider.local');
    });

    it('should validate demo user structure', () => {
      const demo = createAuthTestUsers.demo();
      
      expect(demo.id).toBe('2');
      expect(demo.username).toBe('demo');
      expect(demo.role).toBe('TRADER');
      expect(demo.permissions).toContain('trading.execute');
      expect(demo.permissions).not.toContain('system.admin');
    });

    it('should validate viewer user structure', () => {
      const viewer = createAuthTestUsers.viewer();
      
      expect(viewer.id).toBe('3');
      expect(viewer.username).toBe('viewer');
      expect(viewer.role).toBe('VIEWER');
      expect(viewer.permissions).toContain('trading.view');
      expect(viewer.permissions).not.toContain('trading.execute');
    });

    it('should validate custom user factory', () => {
      const customUser = createAuthTestUsers.custom({
        username: 'custom-test',
        role: 'ADMIN',
        permissions: ['custom.permission']
      });
      
      expect(customUser.username).toBe('custom-test');
      expect(customUser.role).toBe('ADMIN');
      expect(customUser.permissions).toEqual(['custom.permission']);
    });

    it('should validate invalid user factory for error testing', () => {
      const invalid = createAuthTestUsers.invalid();
      
      expect(invalid.id).toBeUndefined();
      expect(invalid.username).toBe('');
      expect(invalid.email).toBe('invalid-email');
      expect(invalid.role).toBe('UNKNOWN');
    });
  });

  describe('Test Scenario Validation', () => {
    it('should validate admin login scenario structure', () => {
      const scenario = authTestScenarios.adminLogin;
      
      expect(scenario.credentials.username).toBe('admin');
      expect(scenario.credentials.password).toBe('password');
      expect(scenario.expectedUser.role).toBe('ADMIN');
      expect(scenario.expectedRole).toBe('ADMIN');
      expect(scenario.expectedPermissions).toContain('system.admin');
    });

    it('should validate demo login scenario structure', () => {
      const scenario = authTestScenarios.demoLogin;
      
      expect(scenario.credentials.username).toBe('demo');
      expect(scenario.expectedUser.role).toBe('TRADER');
      expect(scenario.expectedRole).toBe('TRADER');
      expect(scenario.expectedPermissions).not.toContain('system.admin');
    });

    it('should validate failure scenarios', () => {
      expect(authTestScenarios.failedLogin.expectedUser).toBeNull();
      expect(authTestScenarios.emptyCredentials.expectedUser).toBeNull();
      expect(authTestScenarios.networkError.expectedUser).toBeNull();
      expect(authTestScenarios.networkError.mockError).toBeInstanceOf(Error);
    });
  });

  describe('Test Assertion Validation', () => {
    it('should validate user assertion helper', () => {
      const testUser = createAuthTestUsers.admin();
      
      // Should not throw for valid user
      expect(() => {
        authTestAssertions.assertValidUser(testUser, testUser);
      }).not.toThrow();
      
      // Should throw for null user
      expect(() => {
        authTestAssertions.assertValidUser(null, testUser);
      }).toThrow();
    });

    it('should validate auth failure assertion helper', () => {
      // Should not throw for null user
      expect(() => {
        authTestAssertions.assertAuthFailure(null);
      }).not.toThrow();
      
      // Should throw for valid user
      expect(() => {
        authTestAssertions.assertAuthFailure(createAuthTestUsers.admin());
      }).toThrow();
    });

    it('should validate JWT assertion helper', () => {
      const testUser = createAuthTestUsers.admin();
      const testToken = {
        id: testUser.id,
        username: testUser.username,
        role: testUser.role,
        permissions: testUser.permissions
      };
      
      // Should not throw for valid token
      expect(() => {
        authTestAssertions.assertValidJWT(testToken, testUser);
      }).not.toThrow();
    });
  });

  describe('Performance Guard Rails', () => {
    it('should validate environment setup performance', async () => {
      const startTime = performance.now();
      
      authTestEnv.setup();
      authTestEnv.validate();
      authTestEnv.teardown();
      
      const endTime = performance.now();
      const executionTime = endTime - startTime;
      
      // Should complete within 20ms
      expect(executionTime).toBeLessThan(20);
    });

    it('should validate test hook performance', async () => {
      const mockAuth = vi.fn().mockResolvedValue(createAuthTestUsers.admin());
      _setTestHook_forceAuthenticate(mockAuth);
      
      const startTime = performance.now();
      
      await authenticateWithBackend('admin', 'password');
      
      const endTime = performance.now();
      const executionTime = endTime - startTime;
      
      // Should complete within 50ms
      expect(executionTime).toBeLessThan(50);
      
      _setTestHook_forceAuthenticate(undefined);
    });
  });

  describe('Integration Validation', () => {
    it('should validate that working authentication patterns remain functional', async () => {
      // This validates that our core working pattern from auth-hook-test.test.ts
      // continues to work and hasn't been broken by changes
      
      const mockAuth = vi.fn();
      _setTestHook_forceAuthenticate(mockAuth);
      
      // Test successful authentication
      mockAuth.mockResolvedValueOnce(createAuthTestUsers.admin());
      const result1 = await authenticateWithBackend('admin', 'password');
      expect(result1).toEqual(createAuthTestUsers.admin());
      expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
      
      // Test failed authentication
      mockAuth.mockResolvedValueOnce(null);
      const result2 = await authenticateWithBackend('invalid', 'wrong');
      expect(result2).toBeNull();
      
      _setTestHook_forceAuthenticate(undefined);
    });

    it('should validate that NextAuth route integration points remain stable', async () => {
      // Validate that the dynamic import pattern still works
      const { authenticateWithBackend: dynamicImport } = await import('../../app/lib/auth/backend-auth');
      
      expect(dynamicImport).toBe(authenticateWithBackend);
      expect(typeof dynamicImport).toBe('function');
    });
  });

  describe('Regression Prevention', () => {
    it('should prevent removal of test hook infrastructure', () => {
      // Validate that critical test infrastructure still exists
      expect(_setTestHook_forceAuthenticate).toBeDefined();
      expect(typeof _setTestHook_forceAuthenticate).toBe('function');
      
      // Validate that test environment class exists
      expect(authTestEnv).toBeDefined();
      expect(typeof authTestEnv.setup).toBe('function');
      expect(typeof authTestEnv.teardown).toBe('function');
      expect(typeof authTestEnv.validate).toBe('function');
    });

    it('should prevent breaking changes to test user factories', () => {
      // Validate that all user factories still exist and work
      expect(createAuthTestUsers.admin).toBeDefined();
      expect(createAuthTestUsers.demo).toBeDefined();
      expect(createAuthTestUsers.viewer).toBeDefined();
      expect(createAuthTestUsers.guest).toBeDefined();
      expect(createAuthTestUsers.custom).toBeDefined();
      expect(createAuthTestUsers.invalid).toBeDefined();
      
      // Validate they return correct types
      const admin = createAuthTestUsers.admin();
      expect(admin).toHaveProperty('id');
      expect(admin).toHaveProperty('username');
      expect(admin).toHaveProperty('role');
      expect(admin).toHaveProperty('permissions');
    });

    it('should prevent breaking changes to environment configuration', () => {
      // Validate critical environment variables are still defined
      const criticalVars = [
        'NEXT_PUBLIC_API_URL',
        'NEXTAUTH_SECRET',
        'DATABASE_URL',
        'SECRET_KEY',
        'COINBASE_SANDBOX',
        'TEST_DATABASE_URL'
      ];
      
      criticalVars.forEach(varName => {
        expect(TEST_ENVIRONMENT_CONFIG).toHaveProperty(varName);
        expect(TEST_ENVIRONMENT_CONFIG[varName as keyof typeof TEST_ENVIRONMENT_CONFIG]).toBeTruthy();
      });
    });
  });
});
