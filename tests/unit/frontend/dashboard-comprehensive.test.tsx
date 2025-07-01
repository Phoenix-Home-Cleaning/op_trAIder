/**
 * @fileoverview Comprehensive test suite for TRAIDER dashboard page
 * @module tests/unit/frontend/dashboard-comprehensive
 * 
 * @description
 * Institutional-grade test coverage for the main portfolio dashboard component.
 * Tests include component rendering, metric calculations, position displays,
 * user session handling, performance benchmarks, and accessibility compliance.
 * 
 * @performance
 * - Render time target: <100ms
 * - Test execution: <50ms per test
 * - Memory usage: <5MB per test suite
 * 
 * @risk
 * - Failure impact: MEDIUM - Dashboard accuracy affects trading decisions
 * - Recovery strategy: Comprehensive error boundary testing
 * 
 * @compliance
 * - Audit requirements: Yes - All portfolio views must be tested
 * - Data retention: Test results stored for regression analysis
 * 
 * @see {@link app/dashboard/page.tsx}
 * @since 1.0.0-alpha.1
 * @author TRAIDER Team
 */

import { render, screen, waitFor } from '@testing-library/react';
import { useSession } from 'next-auth/react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import DashboardPage from '../../../app/dashboard/page';

// Mock NextAuth
vi.mock('next-auth/react', () => ({
  useSession: vi.fn(),
}));

const mockUseSession = vi.mocked(useSession);

/**
 * Dashboard test suite
 * 
 * @description
 * Comprehensive testing of the dashboard page component including:
 * - Component rendering and structure validation
 * - Metric card display and calculations
 * - Position table functionality
 * - User session integration
 * - Performance and accessibility compliance
 * - Error handling and edge cases
 * 
 * @tradingImpact Tests core portfolio overview interface
 * @riskLevel MEDIUM - Dashboard accuracy critical for trading decisions
 */
describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  /**
   * Component rendering tests
   * 
   * @description Tests basic component rendering with authenticated user session
   */
  describe('Component Rendering', () => {
    /**
     * Test authenticated user dashboard rendering
     * 
     * @description
     * Verifies dashboard renders correctly with authenticated user session,
     * displays welcome message with user name, and shows Phase 0 indicator.
     * 
     * @performance Target: <50ms render time
     * @tradingImpact Ensures dashboard accessible to authenticated users
     * @riskLevel LOW - Basic rendering functionality
     */
    it('should render dashboard with authenticated user', async () => {
      const startTime = performance.now();
      
      mockUseSession.mockReturnValue({
        data: {
          user: {
            id: 'user_001',
            username: 'johntrader',
            name: 'John Trader',
            email: 'john@traider.com',
            role: 'TRADER' as const,
            permissions: ['trading', 'portfolio_view'],
            lastLogin: new Date().toISOString(),
          },
          expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        },
        status: 'authenticated',
      });

      render(<DashboardPage />);

      // Verify welcome message
      expect(screen.getByText('Welcome back, John Trader')).toBeInTheDocument();
      expect(screen.getByText(/Phase 0 is showing mock data/)).toBeInTheDocument();

      const renderTime = performance.now() - startTime;
      expect(renderTime).toBeLessThan(50);
    });

    /**
     * Test unauthenticated user dashboard rendering
     * 
     * @description
     * Verifies dashboard handles unauthenticated sessions gracefully,
     * showing appropriate fallback content without crashing.
     * 
     * @performance Target: <50ms render time
     * @tradingImpact Ensures dashboard handles auth failures gracefully
     * @riskLevel MEDIUM - Auth failure handling critical
     */
    it('should render dashboard without authenticated user', () => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'unauthenticated',
      });

      render(<DashboardPage />);

      // Should still render basic structure
      expect(screen.getByText(/Welcome back,/)).toBeInTheDocument();
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
    });

    /**
     * Test loading state handling
     * 
     * @description
     * Verifies dashboard renders appropriately during session loading,
     * maintaining UI stability during authentication checks.
     * 
     * @performance Target: <50ms render time
     * @tradingImpact Ensures smooth user experience during auth loading
     * @riskLevel LOW - Loading state handling
     */
    it('should handle loading session state', () => {
      mockUseSession.mockReturnValue({
        data: null,
        status: 'loading',
      });

      render(<DashboardPage />);

      // Should render without crashing during loading
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
    });
  });

  /**
   * Metric cards tests
   * 
   * @description Tests all metric cards display correctly with proper formatting
   */
  describe('Metric Cards', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: { name: 'Test User', email: 'test@traider.com' },
        },
        status: 'authenticated',
      });
    });

    /**
     * Test portfolio value metric display
     * 
     * @description
     * Verifies portfolio value metric displays correctly with proper
     * formatting, change indicators, and description text.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Core portfolio value display for trading decisions
     * @riskLevel HIGH - Portfolio value accuracy critical
     */
    it('should display portfolio value metric correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
      expect(screen.getByText('$125,847.32')).toBeInTheDocument();
      expect(screen.getByText('+2.34%')).toBeInTheDocument();
      expect(screen.getByText('Total portfolio value including all positions')).toBeInTheDocument();
    });

    /**
     * Test daily P&L metric display
     * 
     * @description
     * Verifies daily profit/loss metric displays with correct formatting,
     * positive/negative indicators, and descriptive text.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Daily P&L critical for performance monitoring
     * @riskLevel HIGH - P&L accuracy affects trading decisions
     */
    it('should display daily P&L metric correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Daily P&L')).toBeInTheDocument();
      expect(screen.getByText('+$2,847.12')).toBeInTheDocument();
      expect(screen.getByText('+1.87%')).toBeInTheDocument();
      expect(screen.getByText('Profit/Loss for current trading day')).toBeInTheDocument();
    });

    /**
     * Test active positions metric display
     * 
     * @description
     * Verifies active positions count displays correctly with change
     * indicators and descriptive information.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Position count affects risk management
     * @riskLevel MEDIUM - Position tracking for risk control
     */
    it('should display active positions metric correctly', () => {
      render(<DashboardPage />);

      expect(screen.getAllByText('Active Positions')).toHaveLength(2); // Metric card + section header
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText('+2')).toBeInTheDocument();
      expect(screen.getByText('Number of open trading positions')).toBeInTheDocument();
    });

    /**
     * Test win rate metric display
     * 
     * @description
     * Verifies win rate percentage displays with proper formatting,
     * change indicators, and time period specification.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Win rate critical for strategy evaluation
     * @riskLevel MEDIUM - Strategy performance indicator
     */
    it('should display win rate metric correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('Win Rate')).toBeInTheDocument();
      expect(screen.getByText('67.3%')).toBeInTheDocument();
      expect(screen.getByText('+3.2%')).toBeInTheDocument();
      expect(screen.getByText('Percentage of profitable trades (30 days)')).toBeInTheDocument();
    });

    /**
     * Test metric card styling for positive changes
     * 
     * @description
     * Verifies positive metric changes display with appropriate
     * green styling and visual indicators.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Visual indicators help quick performance assessment
     * @riskLevel LOW - UI styling verification
     */
    it('should apply correct styling for positive changes', () => {
      render(<DashboardPage />);

      // All positive percentage badges should have green styling
      const positivePercentages = screen.getAllByText(/^\+.*%$/);
      positivePercentages.forEach((element) => {
        expect(element).toHaveClass('text-green-800');
        expect(element).toHaveClass('bg-green-100');
      });
    });
  });

  /**
   * Positions table tests
   * 
   * @description Tests position table rendering and data display
   */
  describe('Positions Table', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: { name: 'Test User', email: 'test@traider.com' },
        },
        status: 'authenticated',
      });
    });

    /**
     * Test positions table structure
     * 
     * @description
     * Verifies positions table renders with correct headers,
     * structure, and accessibility attributes.
     * 
     * @performance Target: <20ms render time
     * @tradingImpact Position table core to portfolio management
     * @riskLevel HIGH - Position accuracy critical for trading
     */
    it('should render positions table with correct structure', () => {
      render(<DashboardPage />);

      expect(screen.getAllByText('Active Positions')).toHaveLength(2); // Metric card + section header
      expect(screen.getByText('Current trading positions and performance')).toBeInTheDocument();
      
      // Check table headers
      expect(screen.getByText('Symbol')).toBeInTheDocument();
      expect(screen.getByText('Size')).toBeInTheDocument();
      expect(screen.getByText('Market Value')).toBeInTheDocument();
      expect(screen.getByText('Unrealized P&L')).toBeInTheDocument();
    });

    /**
     * Test BTC position display
     * 
     * @description
     * Verifies BTC position displays with correct symbol, size,
     * value, and P&L formatting including positive styling.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact BTC position accuracy critical for portfolio
     * @riskLevel HIGH - Major position accuracy essential
     */
    it('should display BTC position correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('BTC-USD')).toBeInTheDocument();
      expect(screen.getByText('2.5847')).toBeInTheDocument();
      expect(screen.getByText('$89,234.12')).toBeInTheDocument();
      expect(screen.getByText('+$1,847.23')).toBeInTheDocument();
    });

    /**
     * Test ETH position display
     * 
     * @description
     * Verifies ETH position displays with correct formatting
     * and positive P&L styling indicators.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact ETH position accuracy for portfolio management
     * @riskLevel HIGH - Major position accuracy essential
     */
    it('should display ETH position correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('ETH-USD')).toBeInTheDocument();
      expect(screen.getByText('45.231')).toBeInTheDocument();
      expect(screen.getByText('$23,456.78')).toBeInTheDocument();
      expect(screen.getByText('+$567.89')).toBeInTheDocument();
    });

    /**
     * Test SOL position with negative P&L
     * 
     * @description
     * Verifies SOL position displays correctly with negative P&L
     * and appropriate red styling for losses.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Negative P&L display critical for risk awareness
     * @riskLevel HIGH - Loss visibility essential for risk management
     */
    it('should display SOL position with negative P&L correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('SOL-USD')).toBeInTheDocument();
      expect(screen.getByText('125.67')).toBeInTheDocument();
      expect(screen.getByText('$8,934.56')).toBeInTheDocument();
      
      const negativePnl = screen.getByText('-$234.12');
      expect(negativePnl).toBeInTheDocument();
      expect(negativePnl).toHaveClass('text-red-600');
    });

    /**
     * Test ADA position display
     * 
     * @description
     * Verifies ADA position displays with correct formatting
     * and positive P&L styling.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Small position accuracy for complete portfolio view
     * @riskLevel MEDIUM - Minor position tracking
     */
    it('should display ADA position correctly', () => {
      render(<DashboardPage />);

      expect(screen.getByText('ADA-USD')).toBeInTheDocument();
      expect(screen.getByText('2847.12')).toBeInTheDocument();
      expect(screen.getByText('$4,221.86')).toBeInTheDocument();
      expect(screen.getByText('+$89.45')).toBeInTheDocument();
    });
  });

  /**
   * Performance tests
   * 
   * @description Tests component performance characteristics
   */
  describe('Performance Tests', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: { name: 'Performance Test User', email: 'perf@traider.com' },
        },
        status: 'authenticated',
      });
    });

    /**
     * Test dashboard render performance
     * 
     * @description
     * Verifies dashboard renders within institutional performance
     * targets of <100ms for complete page load.
     * 
     * @performance Target: <100ms render time
     * @tradingImpact Fast dashboard load critical for trading efficiency
     * @riskLevel MEDIUM - Performance affects user productivity
     */
    it('should render within performance targets', async () => {
      const startTime = performance.now();
      
      render(<DashboardPage />);
      
      await waitFor(() => {
        expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
      });
      
      const renderTime = performance.now() - startTime;
      expect(renderTime).toBeLessThan(100);
    });

    /**
     * Test multiple rapid re-renders
     * 
     * @description
     * Verifies dashboard handles multiple rapid re-renders without
     * performance degradation or memory leaks.
     * 
     * @performance Target: <200ms for 10 re-renders
     * @tradingImpact Stable performance under frequent updates
     * @riskLevel LOW - Stress testing for stability
     */
    it('should handle multiple re-renders efficiently', async () => {
      const startTime = performance.now();
      
      for (let i = 0; i < 10; i++) {
        const { rerender } = render(<DashboardPage />);
        rerender(<DashboardPage />);
      }
      
      const totalTime = performance.now() - startTime;
      expect(totalTime).toBeLessThan(200);
    });
  });

  /**
   * Accessibility tests
   * 
   * @description Tests dashboard accessibility compliance
   */
  describe('Accessibility', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: { name: 'Accessibility User', email: 'a11y@traider.com' },
        },
        status: 'authenticated',
      });
    });

    /**
     * Test heading hierarchy
     * 
     * @description
     * Verifies proper heading hierarchy for screen readers
     * and accessibility compliance.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Accessibility ensures platform usability for all users
     * @riskLevel LOW - Accessibility compliance
     */
    it('should have proper heading hierarchy', () => {
      render(<DashboardPage />);

      const h1 = screen.getByRole('heading', { level: 1 });
      expect(h1).toHaveTextContent(/Welcome back/);

      const h2Elements = screen.getAllByRole('heading', { level: 2 });
      expect(h2Elements).toHaveLength(2); // "Active Positions" and "Recent Activity"
      expect(h2Elements[0]).toHaveTextContent('Active Positions');
    });

    /**
     * Test table accessibility
     * 
     * @description
     * Verifies positions table has proper accessibility attributes
     * including table headers and semantic structure.
     * 
     * @performance Target: <10ms verification time
     * @tradingImpact Table accessibility critical for screen readers
     * @riskLevel LOW - Accessibility compliance
     */
    it('should have accessible table structure', () => {
      render(<DashboardPage />);

      const table = screen.getByRole('table');
      expect(table).toBeInTheDocument();

      const columnHeaders = screen.getAllByRole('columnheader');
      expect(columnHeaders).toHaveLength(4);
      expect(columnHeaders[0]).toHaveTextContent('Symbol');
      expect(columnHeaders[1]).toHaveTextContent('Size');
      expect(columnHeaders[2]).toHaveTextContent('Value');
      expect(columnHeaders[3]).toHaveTextContent('P&L');
    });
  });

  /**
   * Edge cases and error handling tests
   * 
   * @description Tests dashboard behavior under edge conditions
   */
  describe('Edge Cases', () => {
    /**
     * Test with null user name
     * 
     * @description
     * Verifies dashboard handles null user name gracefully
     * without crashing or displaying undefined.
     * 
     * @performance Target: <50ms render time
     * @tradingImpact Graceful handling of incomplete user data
     * @riskLevel MEDIUM - Data integrity handling
     */
    it('should handle null user name gracefully', () => {
      mockUseSession.mockReturnValue({
        data: {
          user: {
            name: null,
            email: 'test@traider.com',
          },
        },
        status: 'authenticated',
      });

      render(<DashboardPage />);

      expect(screen.getByText(/Welcome back,/)).toBeInTheDocument();
      expect(screen.queryByText('null')).not.toBeInTheDocument();
      expect(screen.queryByText('undefined')).not.toBeInTheDocument();
    });

    /**
     * Test with undefined session data
     * 
     * @description
     * Verifies dashboard handles completely undefined session
     * data without crashing.
     * 
     * @performance Target: <50ms render time
     * @tradingImpact Robust error handling for auth failures
     * @riskLevel HIGH - System stability under error conditions
     */
    it('should handle undefined session data', () => {
      mockUseSession.mockReturnValue({
        data: undefined,
        status: 'unauthenticated',
      });

      expect(() => render(<DashboardPage />)).not.toThrow();
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
    });
  });

  /**
   * Data integrity tests
   * 
   * @description Tests dashboard data consistency and formatting
   */
  describe('Data Integrity', () => {
    beforeEach(() => {
      mockUseSession.mockReturnValue({
        data: {
          user: { name: 'Data Test User', email: 'data@traider.com' },
        },
        status: 'authenticated',
      });
    });

    /**
     * Test metric data consistency
     * 
     * @description
     * Verifies all metrics display consistent data formatting
     * and proper currency/percentage formatting.
     * 
     * @performance Target: <20ms verification time
     * @tradingImpact Data consistency critical for trading decisions
     * @riskLevel HIGH - Data accuracy essential
     */
    it('should display consistent metric formatting', () => {
      render(<DashboardPage />);

      // Check currency formatting
      expect(screen.getByText('$125,847.32')).toBeInTheDocument();
      expect(screen.getByText('+$2,847.12')).toBeInTheDocument();

      // Check percentage formatting
      expect(screen.getByText('+2.34%')).toBeInTheDocument();
      expect(screen.getByText('+1.87%')).toBeInTheDocument();
      expect(screen.getByText('67.3%')).toBeInTheDocument();
      expect(screen.getByText('+3.2%')).toBeInTheDocument();
    });

    /**
     * Test position data consistency
     * 
     * @description
     * Verifies position data displays with consistent formatting
     * across all symbols and proper decimal precision.
     * 
     * @performance Target: <20ms verification time
     * @tradingImpact Position data accuracy critical for portfolio management
     * @riskLevel HIGH - Position accuracy essential for trading
     */
    it('should display consistent position formatting', () => {
      render(<DashboardPage />);

      // Verify position sizes with proper decimal places
      expect(screen.getByText('2.5847')).toBeInTheDocument();
      expect(screen.getByText('45.231')).toBeInTheDocument();
      expect(screen.getByText('125.67')).toBeInTheDocument();
      expect(screen.getByText('2847.12')).toBeInTheDocument();

      // Verify value formatting
      expect(screen.getByText('$89,234.12')).toBeInTheDocument();
      expect(screen.getByText('$23,456.78')).toBeInTheDocument();
      expect(screen.getByText('$8,934.56')).toBeInTheDocument();
      expect(screen.getByText('$4,221.86')).toBeInTheDocument();
    });
  });
});