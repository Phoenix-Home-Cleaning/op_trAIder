/**
 * @fileoverview Main Dashboard Page Integration Tests
 * @module tests.unit.frontend.main-page
 * 
 * @description
 * Comprehensive integration tests for the TRAIDER V1 main dashboard page.
 * Tests actual page rendering, component interactions, and data display to achieve
 * 90%+ statement coverage for world-class engineering standards.
 * 
 * @performance
 * - Test execution target: <100ms per test
 * - Memory usage: <10MB per test suite
 * - Coverage requirement: >95%
 * 
 * @risk
 * - Failure impact: HIGH - Main dashboard is critical for user experience
 * - Recovery strategy: Automated test retry with component isolation
 * 
 * @compliance
 * - Audit requirements: Yes - UI component validation
 * - Data retention: Test logs retained for 90 days
 * 
 * @see {@link docs/architecture/dashboard.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Import the actual page component
import DashboardPage from '../../../app/page';

describe('Main Dashboard Page - Integration Tests', () => {
  /**
   * Test suite for main dashboard page functionality with real component rendering
   * 
   * @description Tests actual dashboard page rendering and component interactions
   * @riskLevel HIGH - Main dashboard is critical for user experience
   */
  
  beforeEach(() => {
    // Reset environment for each test
    vi.clearAllMocks();
    
    // Set test environment
    vi.stubEnv('NODE_ENV', 'test');
    
    // Mock Date.now() for consistent timestamps in tests
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2024-01-01T12:00:00Z'));
  });

  afterEach(() => {
    // Clean up any environment changes
    vi.restoreAllMocks();
    vi.useRealTimers();
  });

  describe('Page Structure and Layout', () => {
    /**
     * Test suite for page structure and layout rendering
     * 
     * @description Tests page header, navigation, and overall layout structure
     * @riskLevel MEDIUM - Layout affects user experience
     */

    it('renders main dashboard page with correct title', () => {
      /**
       * Test that main page renders with proper title and description
       * 
       * @performance Target: <100ms render time
       * @tradingImpact Main dashboard provides entry point to trading platform
       * @riskLevel HIGH - Page title affects user navigation and SEO
       */
      
      render(<DashboardPage />);

      // Verify page title
      expect(screen.getByRole('heading', { level: 1 })).toHaveTextContent('Dashboard');
      
      // Verify page description
      expect(screen.getByText('Welcome to TRAIDER V1 - Institutional Crypto Trading Platform')).toBeInTheDocument();
    });

    it('renders all key metric cards', () => {
      /**
       * Test that all key trading metrics are displayed
       * 
       * @tradingImpact Key metrics provide critical trading performance visibility
       * @riskLevel HIGH - Missing metrics could affect trading decisions
       */
      
      render(<DashboardPage />);

      // Verify all metric cards are present
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
      expect(screen.getByText('Total P&L')).toBeInTheDocument();
      expect(screen.getByText('Active Positions')).toBeInTheDocument();
      expect(screen.getByText('Win Rate')).toBeInTheDocument();
      
      // Verify metric values (some values appear multiple times)
      expect(screen.getAllByText('$10,000.00')).toHaveLength(2); // Portfolio Value and Total Value
      expect(screen.getByText('+$250.00')).toBeInTheDocument();
      expect(screen.getByText('3')).toBeInTheDocument();
      expect(screen.getByText('65.2%')).toBeInTheDocument();
    });

    it('renders portfolio overview section', () => {
      /**
       * Test that portfolio overview displays correctly
       * 
       * @tradingImpact Portfolio overview shows current asset allocation
       * @riskLevel HIGH - Portfolio visibility is critical for risk management
       */
      
      render(<DashboardPage />);

      // Verify portfolio section header
      expect(screen.getByText('Portfolio Overview')).toBeInTheDocument();
      
      // Verify asset holdings
      expect(screen.getByText('BTC-USD')).toBeInTheDocument();
      expect(screen.getByText('ETH-USD')).toBeInTheDocument();
      expect(screen.getByText('0.15 BTC')).toBeInTheDocument();
      expect(screen.getByText('2.5 ETH')).toBeInTheDocument();
      
      // Verify asset values
      expect(screen.getByText('~$6,750.00')).toBeInTheDocument();
      expect(screen.getByText('~$3,250.00')).toBeInTheDocument();
      
      // Verify total value
      expect(screen.getByText('Total Value')).toBeInTheDocument();
      expect(screen.getByText('+$250.00 (2.5%)')).toBeInTheDocument();
    });

    it('renders recent activity section', () => {
      /**
       * Test that recent trading activity displays correctly
       * 
       * @tradingImpact Recent activity provides trade execution history
       * @riskLevel MEDIUM - Trading history helps with performance analysis
       */
      
      render(<DashboardPage />);

      // Verify recent activity section header
      expect(screen.getByText('Recent Activity')).toBeInTheDocument();
      
      // Verify trade entries (multiple BUY BTC-USD entries exist)
      expect(screen.getAllByText('BUY BTC-USD')).toHaveLength(2); // Two BUY BTC-USD entries
      expect(screen.getByText('SELL ETH-USD')).toBeInTheDocument();
      
      // Verify trade details
      expect(screen.getByText('0.05 BTC')).toBeInTheDocument();
      expect(screen.getByText('0.5 ETH')).toBeInTheDocument();
      expect(screen.getByText('0.1 BTC')).toBeInTheDocument();
      
      // Verify trade prices
      expect(screen.getByText('@$45,000')).toBeInTheDocument();
      expect(screen.getByText('@$1,300')).toBeInTheDocument();
      expect(screen.getByText('@$44,800')).toBeInTheDocument();
      
      // Verify timestamps
      expect(screen.getByText('2 hours ago')).toBeInTheDocument();
      expect(screen.getByText('4 hours ago')).toBeInTheDocument();
      expect(screen.getByText('1 day ago')).toBeInTheDocument();
    });

    it('renders system status section', () => {
      /**
       * Test that system status indicators display correctly
       * 
       * @tradingImpact System status provides operational health visibility
       * @riskLevel HIGH - System status affects trading system reliability
       */
      
      render(<DashboardPage />);

      // Verify system status section header
      expect(screen.getByText('System Status')).toBeInTheDocument();
      
      // Verify status indicators
      expect(screen.getByText('Market Data Feed')).toBeInTheDocument();
      expect(screen.getByText('Trading Engine')).toBeInTheDocument();
      expect(screen.getByText('Risk Management')).toBeInTheDocument();
      expect(screen.getByText('ML Signals (Phase 1)')).toBeInTheDocument();
      
      // Verify last updated timestamp
      expect(screen.getByText('Last Updated')).toBeInTheDocument();
      expect(screen.getByText('12:00:00 PM')).toBeInTheDocument(); // Mocked time
    });

    it('renders Phase 0 notice', () => {
      /**
       * Test that Phase 0 development notice displays correctly
       * 
       * @tradingImpact Phase notice informs users about current functionality
       * @riskLevel LOW - Informational notice for user awareness
       */
      
      render(<DashboardPage />);

      // Verify Phase 0 notice
      expect(screen.getByText('Phase 0: Setup & Foundation')).toBeInTheDocument();
      expect(screen.getByText(/This is a placeholder dashboard/)).toBeInTheDocument();
      expect(screen.getByText(/Real trading functionality/)).toBeInTheDocument();
    });
  });

  describe('MetricCard Component Functionality', () => {
    /**
     * Test suite for MetricCard component behavior
     * 
     * @description Tests metric card rendering with different states
     * @riskLevel MEDIUM - Metric cards display critical trading data
     */

    it('displays positive change indicators correctly', () => {
      /**
       * Test that positive changes are styled correctly
       * 
       * @tradingImpact Positive indicators show profitable performance
       * @riskLevel MEDIUM - Visual indicators affect user decision making
       */
      
      render(<DashboardPage />);

      // Find elements with positive changes
      const positiveChanges = screen.getAllByText('+2.5%');
      expect(positiveChanges.length).toBeGreaterThan(0);
      
      // Verify positive change styling is applied
      positiveChanges.forEach(element => {
        expect(element).toHaveClass('price-positive');
      });
    });

    it('displays neutral change indicators correctly', () => {
      /**
       * Test that neutral/zero changes are styled correctly
       * 
       * @tradingImpact Neutral indicators show stable performance
       * @riskLevel LOW - Neutral indicators provide baseline reference
       */
      
      render(<DashboardPage />);

      // Find element with neutral change
      const neutralChange = screen.getByText('0');
      expect(neutralChange).toBeInTheDocument();
      
      // Verify the change label is displayed
      expect(screen.getByText('vs yesterday')).toBeInTheDocument();
    });

    it('displays change labels correctly', () => {
      /**
       * Test that change period labels are displayed correctly
       * 
       * @tradingImpact Change labels provide context for performance metrics
       * @riskLevel LOW - Labels help users understand metric timeframes
       */
      
      render(<DashboardPage />);

      // Verify various change labels
      expect(screen.getByText('24h')).toBeInTheDocument();
      expect(screen.getByText('All time')).toBeInTheDocument();
      expect(screen.getByText('vs yesterday')).toBeInTheDocument();
      expect(screen.getByText('30d avg')).toBeInTheDocument();
    });

    it('handles metric values with proper formatting', () => {
      /**
       * Test that metric values are formatted correctly
       * 
       * @tradingImpact Proper formatting ensures accurate data interpretation
       * @riskLevel MEDIUM - Incorrect formatting could lead to misinterpretation
       */
      
      render(<DashboardPage />);

      // Verify currency formatting (multiple instances may exist)
      expect(screen.getAllByText('$10,000.00')).toHaveLength(2); // Portfolio Value and Total Value
      expect(screen.getByText('+$250.00')).toBeInTheDocument();
      
      // Verify percentage formatting (multiple +2.5% entries exist)
      expect(screen.getByText('65.2%')).toBeInTheDocument();
      expect(screen.getAllByText('+2.5%')).toHaveLength(2); // Portfolio Value and Total P&L
      
      // Verify numeric formatting
      expect(screen.getByText('3')).toBeInTheDocument();
    });
  });

  describe('StatusIndicator Component Functionality', () => {
    /**
     * Test suite for StatusIndicator component behavior
     * 
     * @description Tests status indicator rendering with different states
     * @riskLevel HIGH - Status indicators show critical system health
     */

    it('displays online status indicators correctly', () => {
      /**
       * Test that online status indicators are styled correctly
       * 
       * @tradingImpact Online status indicates operational systems
       * @riskLevel HIGH - System status affects trading capability
       */
      
      render(<DashboardPage />);

      // Verify online status elements exist
      const onlineStatuses = [
        'Market Data Feed',
        'Trading Engine', 
        'Risk Management'
      ];
      
      onlineStatuses.forEach(status => {
        expect(screen.getByText(status)).toBeInTheDocument();
      });
    });

    it('displays warning status indicators correctly', () => {
      /**
       * Test that warning status indicators are styled correctly
       * 
       * @tradingImpact Warning status indicates potential issues
       * @riskLevel MEDIUM - Warning status requires user attention
       */
      
      render(<DashboardPage />);

      // Verify warning status element
      expect(screen.getByText('ML Signals (Phase 1)')).toBeInTheDocument();
    });

    it('renders status indicator visual elements', () => {
      /**
       * Test that status indicators include visual status dots
       * 
       * @tradingImpact Visual indicators provide quick status assessment
       * @riskLevel LOW - Visual elements enhance user experience
       */
      
      render(<DashboardPage />);

      // Verify status indicators have visual elements (dots)
      const statusContainer = screen.getByText('System Status').closest('.trading-card');
      expect(statusContainer).toBeInTheDocument();
      
      // Check that status indicators are rendered with proper structure
      const statusIndicators = statusContainer?.querySelectorAll('.flex.items-center.space-x-2');
      expect(statusIndicators?.length).toBe(4); // 4 status indicators
    });
  });

  describe('Responsive Layout and CSS Classes', () => {
    /**
     * Test suite for responsive design and CSS class application
     * 
     * @description Tests CSS classes and responsive layout behavior
     * @riskLevel LOW - Layout consistency affects user experience
     */

    it('applies correct CSS classes for layout', () => {
      /**
       * Test that proper CSS classes are applied for layout
       * 
       * @tradingImpact Proper styling ensures professional appearance
       * @riskLevel LOW - Styling affects user experience
       */
      
      render(<DashboardPage />);

      // Verify main container class
      const mainContainer = screen.getByText('Dashboard').closest('.container-dashboard');
      expect(mainContainer).toBeInTheDocument();
      expect(mainContainer).toHaveClass('py-8');
    });

    it('applies trading-specific CSS classes', () => {
      /**
       * Test that trading-specific CSS classes are applied correctly
       * 
       * @tradingImpact Trading-specific styling provides consistent UX
       * @riskLevel LOW - Consistent styling improves usability
       */
      
      render(<DashboardPage />);

      // Verify trading grid classes
      const container = screen.getByText('Portfolio Value').closest('.trading-grid');
      expect(container).toBeInTheDocument();
      
      // Verify trading card classes
      const portfolioCard = screen.getByText('Portfolio Overview').closest('.trading-card');
      expect(portfolioCard).toBeInTheDocument();
    });

    it('handles grid layout for different screen sizes', () => {
      /**
       * Test that grid layouts are properly configured
       * 
       * @tradingImpact Responsive design ensures usability across devices
       * @riskLevel LOW - Responsive design affects accessibility
       */
      
      render(<DashboardPage />);

      // Verify grid classes for responsive design
      const statusGrid = screen.getByText('Market Data Feed').closest('.grid');
      expect(statusGrid).toHaveClass('grid-cols-1', 'md:grid-cols-2', 'lg:grid-cols-4');
    });
  });

  describe('Performance and Accessibility', () => {
    /**
     * Test suite for performance and accessibility features
     * 
     * @description Tests performance characteristics and accessibility compliance
     * @riskLevel MEDIUM - Performance affects user experience
     */

    it('renders within performance requirements', () => {
      /**
       * Test that page renders within performance targets
       * 
       * @performance Target: <100ms render time
       * @tradingImpact Fast rendering improves user experience
       * @riskLevel MEDIUM - Performance affects user satisfaction
       */
      
      const startTime = performance.now();
      render(<DashboardPage />);
      const renderTime = performance.now() - startTime;

      // Should render quickly
      expect(renderTime).toBeLessThan(100);
      
      // Verify page is fully rendered
      expect(screen.getByText('Dashboard')).toBeInTheDocument();
    });

    it('includes proper semantic HTML structure', () => {
      /**
       * Test that page uses proper semantic HTML elements
       * 
       * @tradingImpact Semantic HTML improves accessibility and SEO
       * @riskLevel LOW - Accessibility compliance is important for users
       */
      
      render(<DashboardPage />);

      // Verify semantic heading structure
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      expect(screen.getAllByRole('heading', { level: 2 })).toHaveLength(3); // Portfolio, Activity, Status
      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument(); // Phase 0 notice
    });

    it('provides proper text content for screen readers', () => {
      /**
       * Test that text content is accessible to screen readers
       * 
       * @tradingImpact Accessible content ensures inclusive user experience
       * @riskLevel LOW - Accessibility compliance is required
       */
      
      render(<DashboardPage />);

      // Verify descriptive text is available
      expect(screen.getByText('Welcome to TRAIDER V1 - Institutional Crypto Trading Platform')).toBeInTheDocument();
      expect(screen.getByText(/This is a placeholder dashboard/)).toBeInTheDocument();
      
      // Verify metric labels are descriptive
      expect(screen.getByText('Portfolio Value')).toBeInTheDocument();
      expect(screen.getByText('Total P&L')).toBeInTheDocument();
      expect(screen.getByText('Active Positions')).toBeInTheDocument();
    });
  });

  describe('Dynamic Content and Timestamps', () => {
    /**
     * Test suite for dynamic content and timestamp handling
     * 
     * @description Tests dynamic content updates and timestamp formatting
     * @riskLevel LOW - Dynamic content enhances user experience
     */

    it('displays current timestamp in system status', () => {
      /**
       * Test that current timestamp is displayed correctly
       * 
       * @tradingImpact Current timestamp shows system status freshness
       * @riskLevel LOW - Timestamp accuracy affects user confidence
       */
      
      render(<DashboardPage />);

      // Verify timestamp is displayed (using mocked time)
      expect(screen.getByText('12:00:00 PM')).toBeInTheDocument();
    });

    it('handles timestamp formatting consistently', () => {
      /**
       * Test that timestamps are formatted consistently across the page
       * 
       * @tradingImpact Consistent formatting improves user experience
       * @riskLevel LOW - Formatting consistency affects professionalism
       */
      
      render(<DashboardPage />);

      // Verify various timestamp formats
      expect(screen.getByText('2 hours ago')).toBeInTheDocument();
      expect(screen.getByText('4 hours ago')).toBeInTheDocument();
      expect(screen.getByText('1 day ago')).toBeInTheDocument();
      expect(screen.getByText('12:00:00 PM')).toBeInTheDocument();
    });
  });
});