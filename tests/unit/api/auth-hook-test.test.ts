/**
 * @fileoverview Direct test of authentication test hook
 * @module tests/unit/api/auth-hook-test.test
 *
 * @description
 * Verifies that the dependency injection test hook works correctly.
 *
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import {
  authenticateWithBackend,
  _setTestHook_forceAuthenticate,
} from '../../../apps/frontend/lib/auth/backend-auth';
import { createTestUsers } from '../../setup/prepareAuthTest';

describe('Authentication Test Hook', () => {
  let mockAuth: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockAuth = vi.fn();
  });

  afterEach(() => {
    _setTestHook_forceAuthenticate(undefined);
    vi.restoreAllMocks();
  });

  it('should use the test hook when set', async () => {
    // Setup the test hook
    _setTestHook_forceAuthenticate(mockAuth);

    // Setup mock response
    mockAuth.mockResolvedValueOnce(createTestUsers.admin());

    // Call the function
    const result = await authenticateWithBackend('admin', 'password');

    // Verify the mock was called
    expect(mockAuth).toHaveBeenCalledWith('admin', 'password');
    expect(result).toEqual(createTestUsers.admin());
  });

  it('should use production logic when hook is not set', async () => {
    // Don't set the test hook

    // This should try to make a real HTTP request and fail
    const result = await authenticateWithBackend('admin', 'password');

    // Should return null due to connection failure
    expect(result).toBeNull();
    expect(mockAuth).not.toHaveBeenCalled();
  });

  it('should reset to production logic after clearing hook', async () => {
    // Setup the test hook first
    _setTestHook_forceAuthenticate(mockAuth);
    mockAuth.mockResolvedValueOnce(createTestUsers.admin());

    // Verify hook works
    let result = await authenticateWithBackend('admin', 'password');
    expect(result).toEqual(createTestUsers.admin());
    expect(mockAuth).toHaveBeenCalledWith('admin', 'password');

    // Clear the hook
    _setTestHook_forceAuthenticate(undefined);

    // Now should use production logic
    result = await authenticateWithBackend('admin', 'password');
    expect(result).toBeNull(); // Should fail due to no backend
  });
});
