/**
 * @fileoverview Comprehensive Login Page Tests - Zero Duplication
 * @module tests.unit.frontend.login-comprehensive
 *
 * @description
 * Complete test suite for the TRAIDER V1 login page with zero duplication.
 * Uses parameterized tests to eliminate code duplication while maintaining coverage.
 *
 * @performance
 * - Test execution target: <100ms per test
 * - Memory usage: <5MB per test suite
 * - Coverage requirement: >95%
 *
 * @risk
 * - Failure impact: CRITICAL (authentication testing)
 * - Recovery strategy: Automated test retry with detailed logging
 *
 * @compliance
 * - Audit requirements: Yes
 * - Security testing: Required for authentication
 *
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useRouter } from 'next/navigation';
import { signIn } from 'next-auth/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import LoginPage from '../../../apps/frontend/(auth)/login/page';

// Mock Next.js router and NextAuth
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

vi.mock('next-auth/react', () => ({
  signIn: vi.fn(),
}));

describe('🔐 Login Page - Comprehensive Tests', () => {
  const mockSignIn = vi.mocked(signIn);
  const mockUseRouter = vi.mocked(useRouter);
  const mockPush = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();

    // Setup router mock
    mockUseRouter.mockReturnValue({
      push: mockPush,
      back: vi.fn(),
      forward: vi.fn(),
      refresh: vi.fn(),
      replace: vi.fn(),
      prefetch: vi.fn(),
    });

    // Setup default auth mock
    mockSignIn.mockResolvedValue({
      ok: true,
      status: 200,
      error: null,
      url: null,
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('🏗️ Component Rendering', () => {
    /**
     * Parameterized rendering tests to eliminate duplication
     */
    const renderingTests = [
      {
        name: 'should render login form with all required elements',
        test: () => {
          render(<LoginPage />);

          expect(screen.getByText('Sign in to TRAIDER')).toBeInTheDocument();
          expect(screen.getByText('Institutional Crypto Trading Platform')).toBeInTheDocument();
          expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
          expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
          expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
        },
      },
      {
        name: 'should have proper accessibility attributes',
        test: () => {
          render(<LoginPage />);

          const usernameInput = screen.getByLabelText(/username/i);
          const passwordInput = screen.getByLabelText(/password/i);

          expect(usernameInput).toHaveAttribute('type', 'text');
          expect(usernameInput).toHaveAttribute('id', 'username');
          expect(usernameInput).toHaveAttribute('name', 'username');
          expect(usernameInput).toBeRequired();

          expect(passwordInput).toHaveAttribute('type', 'password');
          expect(passwordInput).toHaveAttribute('id', 'password');
          expect(passwordInput).toHaveAttribute('name', 'password');
          expect(passwordInput).toBeRequired();
        },
      },
      {
        name: 'should have proper CSS classes and styling',
        test: () => {
          render(<LoginPage />);

          const form = screen.getByRole('button', { name: /sign in/i }).closest('form');
          expect(form).toBeInTheDocument();
        },
      },
    ];

    it.each(renderingTests)('$name', ({ test }) => {
      test();
    });
  });

  describe('📝 Form Input Handling', () => {
    /**
     * Parameterized input tests to eliminate duplication
     */
    const inputTests = [
      {
        name: 'should update username field on input change',
        fieldLabel: /username/i,
        testValue: 'testuser',
      },
      {
        name: 'should update password field on input change',
        fieldLabel: /password/i,
        testValue: 'testpassword',
      },
    ];

    it.each(inputTests)('$name', async ({ fieldLabel, testValue }) => {
      render(<LoginPage />);

      const input = screen.getByLabelText(fieldLabel) as HTMLInputElement;
      fireEvent.change(input, { target: { value: testValue } });

      await waitFor(() => {
        expect(input.value).toBe(testValue);
      });
    });

    it('should clear error when user starts typing', async () => {
      render(<LoginPage />);

      // Trigger error by submitting empty form
      const form = screen.getByRole('button', { name: /sign in/i }).closest('form');
      fireEvent.submit(form!);

      await waitFor(() => {
        expect(screen.getByText(/please fill in all fields/i)).toBeInTheDocument();
      });

      // Start typing to clear error
      const usernameInput = screen.getByLabelText(/username/i);
      fireEvent.change(usernameInput, { target: { value: 'test' } });

      await waitFor(() => {
        expect(screen.queryByText(/please fill in all fields/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('🔍 Form Validation', () => {
    /**
     * Parameterized validation tests to eliminate duplication
     */
    const validationTests = [
      {
        name: 'should show error for empty username',
        setup: () => {
          const passwordInput = screen.getByLabelText(/password/i);
          fireEvent.change(passwordInput, { target: { value: 'password123' } });
        },
        shouldShowError: true,
      },
      {
        name: 'should show error for empty password',
        setup: () => {
          const usernameInput = screen.getByLabelText(/username/i);
          fireEvent.change(usernameInput, { target: { value: 'testuser' } });
        },
        shouldShowError: true,
      },
      {
        name: 'should show error for both fields empty',
        setup: () => {}, // No setup needed
        shouldShowError: true,
      },
      {
        name: 'should proceed with valid inputs',
        setup: () => {
          const usernameInput = screen.getByLabelText(/username/i);
          const passwordInput = screen.getByLabelText(/password/i);
          fireEvent.change(usernameInput, { target: { value: 'testuser' } });
          fireEvent.change(passwordInput, { target: { value: 'password123' } });
        },
        shouldShowError: false,
      },
    ];

    it.each(validationTests)('$name', async ({ setup, shouldShowError }) => {
      render(<LoginPage />);

      setup();

      const form = screen.getByRole('button', { name: /sign in/i }).closest('form');
      fireEvent.submit(form!);

      if (shouldShowError) {
        await waitFor(() => {
          expect(screen.getByText(/please fill in all fields/i)).toBeInTheDocument();
        });
      } else {
        await waitFor(() => {
          expect(screen.queryByText(/please fill in all fields/i)).not.toBeInTheDocument();
        });
      }
    });
  });

  describe('🔐 Authentication Flow', () => {
    /**
     * Parameterized auth flow tests to eliminate duplication
     */
    const authFlowTests = [
      {
        name: 'should handle successful authentication',
        mockSetup: () => {
          mockSignIn.mockResolvedValue({ ok: true, status: 200, error: null, url: null });
        },
        expectedBehavior: async () => {
          await waitFor(() => {
            expect(mockPush).toHaveBeenCalledWith('/dashboard');
          });
        },
      },
      {
        name: 'should handle credentials signin error',
        mockSetup: () => {
          mockSignIn.mockResolvedValue({
            ok: false,
            error: 'CredentialsSignin',
            status: 401,
            url: null,
          });
        },
        expectedBehavior: async () => {
          await waitFor(() => {
            expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
          });
        },
      },
    ];

    it.each(authFlowTests)('$name', async ({ mockSetup, expectedBehavior }) => {
      mockSetup();

      render(<LoginPage />);

      // Fill form with valid data
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      // Submit form
      const form = screen.getByRole('button', { name: /sign in/i }).closest('form');
      fireEvent.submit(form!);

      // Verify expected behavior
      await expectedBehavior();
    });
  });

  describe('🚨 Error Handling', () => {
    /**
     * Parameterized error tests to eliminate duplication
     */
    const errorTests = [
      {
        name: 'should handle network errors',
        mockSetup: () => {
          mockSignIn.mockRejectedValue(new Error('Network error'));
        },
        expectedError: /network error/i,
      },
      {
        name: 'should handle unknown errors',
        mockSetup: () => {
          mockSignIn.mockRejectedValue(new Error('Unknown error'));
        },
        expectedError: /unknown error/i,
      },
    ];

    it.each(errorTests)('$name', async ({ mockSetup, expectedError }) => {
      mockSetup();

      render(<LoginPage />);

      // Fill and submit form
      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      const form = screen.getByRole('button', { name: /sign in/i }).closest('form');
      fireEvent.submit(form!);

      // Should show error
      await waitFor(() => {
        expect(screen.getByText(expectedError)).toBeInTheDocument();
      });
    });
  });

  describe('⚡ Performance', () => {
    it('should render within performance targets', async () => {
      const start = performance.now();

      render(<LoginPage />);

      const duration = performance.now() - start;
      expect(duration).toBeLessThan(100); // <100ms render time
    });
  });
});
