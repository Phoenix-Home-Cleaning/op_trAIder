/**
 * @fileoverview Central authentication test utilities for TRAIDER V1
 * @module tests/setup/prepareAuthTest
 *
 * @description
 * Provides clean, deterministic authentication mocking for unit tests.
 * Uses dependency injection to avoid brittle global mocks.
 *
 * @performance
 * - Setup time: <5ms
 * - Mock execution: <1ms
 * - Memory usage: <1MB
 *
 * @risk
 * - Failure impact: LOW - Test utility only
 * - Recovery strategy: Reset hooks in afterEach
 *
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { afterEach, beforeEach, vi } from 'vitest';
import { _setTestHook_forceAuthenticate } from '../../app/lib/auth/backend-auth';
import type { User } from 'next-auth';

/**
 * Setup authentication mocking for tests
 *
 * @description
 * Provides clean authentication mocking with proper setup/teardown.
 * Returns a mock function that can be configured per test.
 *
 * @returns Mock function for authentication
 *
 * @example
 * ```typescript
 * const mockAuth = withAuthMock();
 *
 * mockAuth.mockResolvedValueOnce({
 *   id: '1',
 *   username: 'admin',
 *   role: 'ADMIN',
 *   // ...
 * });
 * ```
 */
export function withAuthMock() {
  let mockAuthFn: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    // Create fresh mock function
    mockAuthFn = vi.fn();

    // Install the test hook
    _setTestHook_forceAuthenticate(mockAuthFn);

    // Set safe environment defaults
    process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8000';
    process.env.NEXTAUTH_SECRET = 'unit-test-secret-key-for-testing-only';
    // Note: NODE_ENV is read-only in some environments, so we skip setting it
  });

  afterEach(() => {
    // Clean up the test hook
    _setTestHook_forceAuthenticate(undefined);

    // Restore all mocks
    vi.restoreAllMocks();
  });

  // Return accessor function for the mock
  return () => {
    if (!mockAuthFn) {
      throw new Error('withAuthMock must be called in a test context');
    }
    return mockAuthFn;
  };
}

/**
 * Create standard test user objects
 *
 * @description
 * Factory functions for creating consistent test user data.
 * Reduces test boilerplate and ensures consistent test data.
 */
export const createTestUsers = {
  admin: (): User => ({
    id: '1',
    username: 'admin',
    name: 'admin',
    email: 'admin@traider.local',
    role: 'ADMIN',
    permissions: ['trading.execute', 'trading.view', 'risk.manage', 'system.admin'],
    lastLogin: '2024-01-01T00:00:00.000Z',
  }),

  demo: (): User => ({
    id: '2',
    username: 'demo',
    name: 'demo',
    email: 'demo@traider.local',
    role: 'TRADER',
    permissions: ['trading.execute', 'trading.view', 'risk.view'],
    lastLogin: '2024-01-01T00:00:00.000Z',
  }),

  viewer: (): User => ({
    id: '3',
    username: 'viewer',
    name: 'viewer',
    email: 'viewer@traider.local',
    role: 'VIEWER',
    permissions: ['trading.view'],
    lastLogin: '2024-01-01T00:00:00.000Z',
  }),

  custom: (overrides: Partial<User>): User => ({
    id: '999',
    username: 'custom',
    name: 'custom',
    email: 'custom@traider.local',
    role: 'VIEWER',
    permissions: [],
    lastLogin: '2024-01-01T00:00:00.000Z',
    ...overrides,
  }),
};
