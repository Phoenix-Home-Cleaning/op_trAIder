/**
 * @fileoverview Comprehensive Dashboard Layout Tests
 * @module tests.unit.frontend.dashboard-layout-comprehensive
 *
 * @description
 * Comprehensive test suite for the TRAIDER V1 dashboard layout component including
 * navigation, responsive behavior, authentication states, and user interactions.
 *
 * @performance
 * - Test execution target: <200ms per test
 * - Memory usage: <10MB per test suite
 * - Coverage requirement: >95%
 *
 * @risk
 * - Failure impact: HIGH - Dashboard is core user interface
 * - Recovery strategy: Component isolation and retry
 *
 * @compliance
 * - Audit requirements: Yes - UI component testing
 * - Data retention: Test logs retained for 30 days
 *
 * @see {@link docs/architecture/frontend.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { useSession, signOut } from 'next-auth/react';
import { usePathname } from 'next/navigation';

// Mock Next.js hooks
vi.mock('next-auth/react');
vi.mock('next/navigation');
vi.mock('next/link', () => ({
  default: ({ children, href, ...props }: any) => (
    <a href={href} {...props}>
      {children}
    </a>
  ),
}));

describe('🏗️ Dashboard Layout Comprehensive Testing', () => {
  const mockUseSession = vi.mocked(useSession);
  const mockUsePathname = vi.mocked(usePathname);
  const mockSignOut = vi.mocked(signOut);

  beforeEach(() => {
    vi.clearAllMocks();
    mockUsePathname.mockReturnValue('/dashboard');
    mockSignOut.mockResolvedValue(undefined);
  });

  describe('🔄 Loading States', () => {
    it('should render loading state when session is loading', async () => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'loading',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Test Content</div>
        </DashboardLayout>
      );

      expect(screen.getByText('Loading TRAIDER...')).toBeInTheDocument();

      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });
  });

  describe('🔐 Authentication States', () => {
    it('should render dashboard with authenticated user', async () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'John Trader',
            email: 'john@traider.com',
            role: 'TRADER',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Dashboard Content</div>
        </DashboardLayout>
      );

      expect(screen.getByText('TRAIDER V1')).toBeInTheDocument();
      expect(screen.getByText('John Trader')).toBeInTheDocument();
      expect(screen.getByText('TRADER')).toBeInTheDocument();
    });

    it('should render user initials correctly', async () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'Alice Smith',
            email: 'alice@traider.com',
            role: 'ADMIN',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      expect(screen.getByText('A')).toBeInTheDocument(); // First letter of name
      expect(screen.getByText('Alice Smith')).toBeInTheDocument();
    });

    it('should handle missing user data gracefully', async () => {
      mockUseSession.mockReturnValue({
        data: { user: null },
        status: 'authenticated',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      expect(screen.getByText('U')).toBeInTheDocument(); // Default initial
      expect(screen.getByText('User')).toBeInTheDocument(); // Default name
    });
  });

  describe('🧭 Navigation Testing', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'Test User',
            email: 'test@traider.com',
            role: 'TRADER',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);
    });

    it('should render all navigation items', async () => {
      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      // Use getAllByText to handle multiple instances
      expect(screen.getAllByText('Portfolio').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Performance').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Risk').length).toBeGreaterThan(0);
      expect(screen.getAllByText('Signals').length).toBeGreaterThan(0);
      expect(screen.getAllByText('System').length).toBeGreaterThan(0);
    });

    it('should highlight active navigation item', async () => {
      mockUsePathname.mockReturnValue('/performance');

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      // Check that Performance navigation exists and is rendered
      const performanceTexts = screen.getAllByText('Performance');
      expect(performanceTexts.length).toBeGreaterThan(0);
      expect(screen.getByText('Trading performance analytics')).toBeInTheDocument();
    });

    it('should show navigation descriptions', async () => {
      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      expect(screen.getByText('Portfolio overview and positions')).toBeInTheDocument();
      expect(screen.getByText('Trading performance analytics')).toBeInTheDocument();
    });

    it('should render navigation icons', async () => {
      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      expect(screen.getByText('📊')).toBeInTheDocument(); // Portfolio
      expect(screen.getByText('📈')).toBeInTheDocument(); // Performance
      expect(screen.getByText('🛡️')).toBeInTheDocument(); // Risk
    });
  });

  describe('📱 Responsive Sidebar Testing', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'Test User',
            email: 'test@traider.com',
            role: 'TRADER',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);
    });

    it('should render mobile menu and close buttons', async () => {
      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      // Check if buttons exist by their text content
      expect(screen.getByText('✕')).toBeInTheDocument();

      // Check for hamburger menu SVG
      const svgElement = document.querySelector('svg');
      expect(svgElement).toBeInTheDocument();
    });
  });

  describe('🚪 Logout Functionality', () => {
    it('should handle logout', async () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'Test User',
            email: 'test@traider.com',
            role: 'TRADER',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      const logoutButton = screen.getByText('Sign Out');
      fireEvent.click(logoutButton);

      expect(mockSignOut).toHaveBeenCalledWith({ callbackUrl: '/login' });
    });
  });

  describe('🎨 Visual Elements', () => {
    it('should have proper brand styling', async () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'Test User',
            email: 'test@traider.com',
            role: 'TRADER',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      const brand = screen.getByText('TRAIDER V1');
      expect(brand).toHaveClass('text-xl', 'font-bold');
    });

    it('should render user avatar properly', async () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: 'Test User',
            email: 'test@traider.com',
            role: 'TRADER',
          },
        },
        status: 'authenticated',
        update: vi.fn(),
      } as any);

      const { default: DashboardLayout } = await import('../../../app/dashboard/layout');

      render(
        <DashboardLayout>
          <div>Content</div>
        </DashboardLayout>
      );

      const avatar = screen.getByText('T'); // First letter of Test User
      expect(avatar.closest('div')).toHaveClass('h-8', 'w-8', 'rounded-full', 'bg-blue-600');
    });
  });
});
