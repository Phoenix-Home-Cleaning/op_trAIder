/**
 * @fileoverview Comprehensive Login Page Tests
 * @module tests.unit.frontend.login-comprehensive
 *
 * @description
 * Complete test suite for the TRAIDER V1 login page including form validation,
 * authentication flows, error handling, and security measures. Achieves >95%
 * coverage for critical authentication component.
 *
 * @performance
 * - Test execution target: <200ms per test
 * - Memory usage: <10MB per test suite
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
import LoginPage from '../../../app/(auth)/login/page';

// Mock Next.js router
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(),
}));

// Mock NextAuth
vi.mock('next-auth/react', () => ({
  signIn: vi.fn(),
}));

describe('🔐 Login Page - Comprehensive Tests', () => {
  const mockPush = vi.fn();
  const mockSignIn = vi.mocked(signIn);
  const mockUseRouter = vi.mocked(useRouter);

  beforeEach(() => {
    // Reset all mocks
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

    // Setup default signIn mock
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
    it('should render login form with all required elements', () => {
      render(<LoginPage />);

      // Check header elements
      expect(screen.getByText('Sign in to TRAIDER')).toBeInTheDocument();
      expect(screen.getByText('Institutional Crypto Trading Platform')).toBeInTheDocument();

      // Check form elements
      expect(screen.getByLabelText(/username/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();

      // Check form structure
      expect(screen.getByRole('form')).toBeInTheDocument();
    });

    it('should have proper accessibility attributes', () => {
      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);

      // Check input attributes
      expect(usernameInput).toHaveAttribute('type', 'text');
      expect(usernameInput).toHaveAttribute('id', 'username');
      expect(usernameInput).toHaveAttribute('name', 'username');

      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(passwordInput).toHaveAttribute('id', 'password');
      expect(passwordInput).toHaveAttribute('name', 'password');

      // Check required attributes
      expect(usernameInput).toBeRequired();
      expect(passwordInput).toBeRequired();
    });

    it('should have proper CSS classes and styling', () => {
      render(<LoginPage />);

      // Check main container
      const container = screen.getByText('Sign in to TRAIDER').closest('div');
      expect(container?.parentElement).toHaveClass(
        'min-h-screen',
        'flex',
        'items-center',
        'justify-center'
      );

      // Check trading card styling
      const cardContent = screen.getByRole('form').closest('.trading-card-content');
      expect(cardContent).toBeInTheDocument();
    });
  });

  describe('📝 Form Input Handling', () => {
    it('should update username field on input change', async () => {
      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;

      fireEvent.change(usernameInput, { target: { value: 'testuser' } });

      await waitFor(() => {
        expect(usernameInput.value).toBe('testuser');
      });
    });

    it('should update password field on input change', async () => {
      render(<LoginPage />);

      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;

      fireEvent.change(passwordInput, { target: { value: 'testpassword' } });

      await waitFor(() => {
        expect(passwordInput.value).toBe('testpassword');
      });
    });

    it('should clear error when user starts typing', async () => {
      render(<LoginPage />);

      // Trigger an error first
      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please fill in all fields/i)).toBeInTheDocument();
      });

      // Start typing in username
      const usernameInput = screen.getByLabelText(/username/i);
      fireEvent.change(usernameInput, { target: { value: 'test' } });

      await waitFor(() => {
        expect(screen.queryByText(/please fill in all fields/i)).not.toBeInTheDocument();
      });
    });

    it('should handle multiple rapid input changes', async () => {
      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;

      // Rapid input changes
      fireEvent.change(usernameInput, { target: { value: 'a' } });
      fireEvent.change(usernameInput, { target: { value: 'ab' } });
      fireEvent.change(usernameInput, { target: { value: 'abc' } });

      await waitFor(() => {
        expect(usernameInput.value).toBe('abc');
      });
    });
  });

  describe('🔍 Form Validation', () => {
    it('should show error for empty username', async () => {
      render(<LoginPage />);

      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Fill only password
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please fill in all fields/i)).toBeInTheDocument();
      });

      // Should not call signIn
      expect(mockSignIn).not.toHaveBeenCalled();
    });

    it('should show error for empty password', async () => {
      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Fill only username
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please fill in all fields/i)).toBeInTheDocument();
      });

      // Should not call signIn
      expect(mockSignIn).not.toHaveBeenCalled();
    });

    it('should show error for both fields empty', async () => {
      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/please fill in all fields/i)).toBeInTheDocument();
      });

      // Should not call signIn
      expect(mockSignIn).not.toHaveBeenCalled();
    });

    it('should proceed with valid inputs', async () => {
      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Fill both fields
      fireEvent.change(usernameInput, { target: { value: 'testuser' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('credentials', {
          username: 'testuser',
          password: 'password123',
          redirect: false,
        });
      });
    });
  });

  describe('🔐 Authentication Flow', () => {
    it('should handle successful authentication', async () => {
      mockSignIn.mockResolvedValue({
        ok: true,
        status: 200,
        error: null,
        url: null,
      });

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should handle credentials signin error', async () => {
      mockSignIn.mockResolvedValue({
        ok: false,
        status: 401,
        error: 'CredentialsSignin',
        url: null,
      });

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid username or password/i)).toBeInTheDocument();
      });

      expect(mockPush).not.toHaveBeenCalled();
    });

    it('should handle callback route error', async () => {
      mockSignIn.mockResolvedValue({
        ok: false,
        status: 500,
        error: 'CallbackRouteError',
        url: null,
      });

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(
          screen.getByText(/authentication service temporarily unavailable/i)
        ).toBeInTheDocument();
      });
    });

    it('should handle unknown authentication errors', async () => {
      mockSignIn.mockResolvedValue({
        ok: false,
        status: 500,
        error: 'UnknownError',
        url: null,
      });

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/login failed. please try again/i)).toBeInTheDocument();
      });
    });

    it('should handle unexpected ok:false without error', async () => {
      mockSignIn.mockResolvedValue({
        ok: false,
        status: 200,
        error: null,
        url: null,
      });

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/unexpected error during login/i)).toBeInTheDocument();
      });
    });
  });

  describe('⚡ Loading States', () => {
    it('should show loading state during authentication', async () => {
      // Mock delayed signIn
      mockSignIn.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  status: 200,
                  error: null,
                  url: null,
                }),
              100
            )
          )
      );

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      // Check loading state
      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();

      // Wait for completion
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should disable form during loading', async () => {
      mockSignIn.mockImplementation(
        () =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  ok: true,
                  status: 200,
                  error: null,
                  url: null,
                }),
              50
            )
          )
      );

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i) as HTMLInputElement;
      const passwordInput = screen.getByLabelText(/password/i) as HTMLInputElement;
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      // Check disabled state
      expect(submitButton).toBeDisabled();
      expect(usernameInput).toBeDisabled();
      expect(passwordInput).toBeDisabled();

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });
  });

  describe('🚨 Error Handling', () => {
    it('should handle network errors', async () => {
      mockSignIn.mockRejectedValue(new Error('Network error'));

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    it('should handle unknown errors', async () => {
      mockSignIn.mockRejectedValue('Unknown error');

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/an unexpected error occurred/i)).toBeInTheDocument();
      });
    });

    it('should reset loading state after error', async () => {
      mockSignIn.mockRejectedValue(new Error('Test error'));

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/test error/i)).toBeInTheDocument();
      });

      // Check that loading state is reset
      expect(submitButton).not.toBeDisabled();
      expect(screen.queryByText(/signing in/i)).not.toBeInTheDocument();
    });
  });

  describe('🔄 User Experience', () => {
    it('should allow retry after error', async () => {
      // First attempt fails
      mockSignIn.mockRejectedValueOnce(new Error('Network error'));

      // Second attempt succeeds
      mockSignIn.mockResolvedValueOnce({
        ok: true,
        status: 200,
        error: null,
        url: null,
      });

      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // First attempt
      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });

      // Second attempt
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    it('should handle form submission via Enter key', async () => {
      render(<LoginPage />);

      const usernameInput = screen.getByLabelText(/username/i);
      const passwordInput = screen.getByLabelText(/password/i);

      fireEvent.change(usernameInput, { target: { value: 'admin' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });

      // Submit via Enter key on password field
      fireEvent.keyDown(passwordInput, { key: 'Enter', code: 'Enter' });

      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('credentials', {
          username: 'admin',
          password: 'password123',
          redirect: false,
        });
      });
    });
  });

  describe('🎨 Visual States', () => {
    it('should display error message with proper styling', async () => {
      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);

      await waitFor(() => {
        const errorMessage = screen.getByText(/please fill in all fields/i);
        expect(errorMessage).toBeInTheDocument();
        expect(errorMessage).toHaveClass('text-destructive');
      });
    });

    it('should show proper button states', () => {
      render(<LoginPage />);

      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Initial state
      expect(submitButton).toHaveClass('btn-primary');
      expect(submitButton).not.toBeDisabled();
    });
  });
});
