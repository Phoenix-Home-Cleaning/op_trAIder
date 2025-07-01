/**
 * @fileoverview Comprehensive tests for Login page component
 * @module tests.unit.frontend.login-comprehensive
 * 
 * @description
 * Institutional-grade test coverage for login page including:
 * - Authentication flow validation
 * - Error handling and user feedback
 * - Form validation and submission
 * - Security considerations
 * - Performance characteristics
 * 
 * @performance
 * - Test execution: <100ms per test
 * - Coverage target: >95%
 * - Memory usage: <20MB
 * 
 * @risk
 * - Failure impact: HIGH - Authentication security
 * - Recovery strategy: Comprehensive validation
 * 
 * @compliance
 * - Audit requirements: All authentication flows tested
 * - Data retention: Test results retained 30 days
 * 
 * @see {@link docs/testing/frontend-authentication.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { signIn, getSession } from 'next-auth/react';
import { useRouter } from 'next/navigation';
import LoginPage from '@/app/(auth)/login/page';

// Mock next-auth
vi.mock('next-auth/react', () => ({
  signIn: vi.fn(),
  getSession: vi.fn(),
  useSession: vi.fn(() => ({
    data: null,
    status: 'unauthenticated'
  }))
}));

// Mock next/navigation
vi.mock('next/navigation', () => ({
  useRouter: vi.fn()
}));

// Mock next/link
vi.mock('next/link', () => {
  return function MockLink({ children, href, ...props }: any) {
    return <a href={href} {...props}>{children}</a>;
  };
});

describe('LoginPage Component', () => {
  const mockPush = vi.fn();
  const mockSignIn = vi.mocked(signIn);
  const mockGetSession = vi.mocked(getSession);
  const mockUseRouter = vi.mocked(useRouter);

  beforeEach(() => {
    mockUseRouter.mockReturnValue({
      push: mockPush,
      replace: vi.fn(),
      refresh: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      prefetch: vi.fn()
    } as any);

    mockSignIn.mockResolvedValue({ 
      ok: true, 
      error: null, 
      status: 200, 
      url: null 
    });
    
    mockGetSession.mockResolvedValue(null);
  });

  afterEach(() => {
    cleanup();
    vi.clearAllMocks();
  });

  describe('Component Rendering', () => {
    /**
     * Test basic component rendering and structure.
     * 
     * @tradingImpact MEDIUM - User interface availability
     * @riskLevel LOW - Basic rendering
     */
    it('should render login form with all required elements', () => {
      render(<LoginPage />);

      // Check for main form elements
      expect(screen.getByRole('heading', { name: /sign in/i })).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
      
      // Check for additional elements
      expect(screen.getByText(/don't have an account/i)).toBeInTheDocument();
      expect(screen.getByText(/forgot password/i)).toBeInTheDocument();
    });

    /**
     * Test TRAIDER branding and institutional appearance.
     * 
     * @tradingImpact LOW - Brand consistency
     * @riskLevel LOW - UI branding
     */
    it('should display TRAIDER branding and institutional styling', () => {
      render(<LoginPage />);

      // Check for TRAIDER branding
      expect(screen.getByText(/traider/i)).toBeInTheDocument();
      
      // Check for institutional messaging
      expect(screen.getByText(/institutional-grade/i) || 
             screen.getByText(/professional trading/i) ||
             screen.getByText(/secure trading platform/i)).toBeInTheDocument();
    });

    /**
     * Test form accessibility features.
     * 
     * @tradingImpact MEDIUM - User accessibility
     * @riskLevel LOW - Accessibility compliance
     */
    it('should have proper accessibility attributes', () => {
      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Check input attributes
      expect(emailInput).toHaveAttribute('type', 'email');
      expect(emailInput).toHaveAttribute('required');
      expect(passwordInput).toHaveAttribute('type', 'password');
      expect(passwordInput).toHaveAttribute('required');
      
      // Check button attributes
      expect(submitButton).toHaveAttribute('type', 'submit');
    });
  });

  describe('Form Validation', () => {
    /**
     * Test email validation with various formats.
     * 
     * @tradingImpact HIGH - Authentication security
     * @riskLevel MEDIUM - Input validation
     */
    it('should validate email format correctly', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Test invalid email formats
      const invalidEmails = [
        'invalid-email',
        'test@',
        '@domain.com',
        'test..test@domain.com',
        'test@domain',
        ''
      ];

      for (const email of invalidEmails) {
        await user.clear(emailInput);
        if (email) {
          await user.type(emailInput, email);
        }
        await user.click(submitButton);

        // Should show validation error
        await waitFor(() => {
          expect(screen.getByText(/invalid email/i) || 
                 screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
        });
      }
    });

    /**
     * Test password validation requirements.
     * 
     * @tradingImpact HIGH - Authentication security
     * @riskLevel HIGH - Password security
     */
    it('should validate password requirements', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter valid email
      await user.type(emailInput, 'test@traider.com');

      // Test empty password
      await user.click(submitButton);
      await waitFor(() => {
        expect(screen.getByText(/password is required/i) || 
               screen.getByText(/please enter your password/i)).toBeInTheDocument();
      });

      // Test minimum length if enforced
      await user.type(passwordInput, '123');
      await user.click(submitButton);
      // Note: Actual validation depends on implementation
    });

    /**
     * Test form submission with valid credentials.
     * 
     * @tradingImpact CRITICAL - Authentication flow
     * @riskLevel MEDIUM - Form submission
     */
    it('should submit form with valid credentials', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter valid credentials
      await user.type(emailInput, 'test@traider.com');
      await user.type(passwordInput, 'validPassword123');
      await user.click(submitButton);

      // Should call signIn with correct parameters
      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalledWith('credentials', {
          email: 'test@traider.com',
          password: 'validPassword123',
          redirect: false
        });
      });
    });
  });

  describe('Authentication Flow', () => {
    /**
     * Test successful authentication flow.
     * 
     * @tradingImpact CRITICAL - User authentication
     * @riskLevel HIGH - Authentication security
     */
    it('should handle successful authentication', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValue({ 
        ok: true, 
        error: null, 
        status: 200, 
        url: null 
      });

      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter credentials and submit
      await user.type(emailInput, 'test@traider.com');
      await user.type(passwordInput, 'validPassword123');
      await user.click(submitButton);

      // Should redirect to dashboard
      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/dashboard');
      });
    });

    /**
     * Test authentication failure handling.
     * 
     * @tradingImpact HIGH - Security error handling
     * @riskLevel HIGH - Authentication errors
     */
    it('should handle authentication failure', async () => {
      const user = userEvent.setup();
      mockSignIn.mockResolvedValue({ 
        ok: false, 
        error: 'CredentialsSignin', 
        status: 401, 
        url: null 
      });

      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter credentials and submit
      await user.type(emailInput, 'test@traider.com');
      await user.type(passwordInput, 'wrongPassword');
      await user.click(submitButton);

      // Should show error message
      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i) || 
               screen.getByText(/authentication failed/i) ||
               screen.getByText(/incorrect email or password/i)).toBeInTheDocument();
      });

      // Should not redirect
      expect(mockPush).not.toHaveBeenCalled();
    });

    /**
     * Test network error handling.
     * 
     * @tradingImpact MEDIUM - Error resilience
     * @riskLevel MEDIUM - Network failures
     */
    it('should handle network errors gracefully', async () => {
      const user = userEvent.setup();
      mockSignIn.mockRejectedValue(new Error('Network error'));

      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter credentials and submit
      await user.type(emailInput, 'test@traider.com');
      await user.type(passwordInput, 'validPassword123');
      await user.click(submitButton);

      // Should show network error message
      await waitFor(() => {
        expect(screen.getByText(/network error/i) || 
               screen.getByText(/connection failed/i) ||
               screen.getByText(/please try again/i)).toBeInTheDocument();
      });
    });

    /**
     * Test loading state during authentication.
     * 
     * @tradingImpact MEDIUM - User experience
     * @riskLevel LOW - Loading states
     */
    it('should show loading state during authentication', async () => {
      const user = userEvent.setup();
      
      // Mock slow authentication
      mockSignIn.mockImplementation(() => 
        new Promise(resolve => 
          setTimeout(() => resolve({ ok: true, error: null, status: 200, url: null }), 1000)
        )
      );

      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Enter credentials and submit
      await user.type(emailInput, 'test@traider.com');
      await user.type(passwordInput, 'validPassword123');
      await user.click(submitButton);

      // Should show loading state
      expect(screen.getByText(/signing in/i) || 
             screen.getByText(/loading/i) ||
             submitButton).toBeDisabled();
    });
  });

  describe('Performance', () => {
    /**
     * Test component rendering performance.
     * 
     * @performance Target: <50ms initial render
     * @tradingImpact MEDIUM - User experience
     * @riskLevel LOW - Performance
     */
    it('should render within performance targets', () => {
      const startTime = performance.now();
      
      render(<LoginPage />);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render in less than 50ms
      expect(renderTime).toBeLessThan(50);
    });

    /**
     * Test form submission performance.
     * 
     * @performance Target: <100ms form processing
     * @tradingImpact MEDIUM - User experience
     * @riskLevel LOW - Performance
     */
    it('should process form submission quickly', async () => {
      const user = userEvent.setup();
      render(<LoginPage />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      // Measure form processing time
      await user.type(emailInput, 'test@traider.com');
      await user.type(passwordInput, 'validPassword123');

      const startTime = performance.now();
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(mockSignIn).toHaveBeenCalled();
      });

      const endTime = performance.now();
      const processingTime = endTime - startTime;

      // Should process in reasonable time
      expect(processingTime).toBeLessThan(100);
    });
  });
});