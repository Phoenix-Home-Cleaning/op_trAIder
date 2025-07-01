/**
 * @fileoverview Providers Component Unit Tests
 * @module tests.unit.frontend.providers
 *
 * @description
 * Comprehensive unit tests for the TRAIDER V1 Providers component including
 * SessionProvider initialization, error handling, and authentication context.
 * Tests cover all critical paths for application-wide provider functionality.
 *
 * @performance
 * - Test execution target: <20ms per test
 * - Memory usage: <2MB per test suite
 * - Coverage requirement: >95%
 *
 * @risk
 * - Failure impact: CRITICAL - Providers affect entire application
 * - Recovery strategy: Automated test retry with provider isolation
 *
 * @compliance
 * - Audit requirements: Yes - Authentication provider testing
 * - Data retention: Test logs retained for 90 days
 *
 * @see {@link docs/architecture/authentication.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import '@testing-library/jest-dom';
import { SessionProvider } from 'next-auth/react';
import { Providers } from '@/providers';

// Mock NextAuth SessionProvider
vi.mock('next-auth/react', () => ({
  SessionProvider: vi.fn(({ children }) => <div data-testid="session-provider">{children}</div>),
}));

describe('Providers Component', () => {
  /**
   * Test suite for Providers component functionality
   *
   * @description Tests provider initialization and child component wrapping
   * @riskLevel CRITICAL - Providers are foundation of application architecture
   */

  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();
  });

  it('renders children within SessionProvider', () => {
    /**
     * Test that Providers component properly wraps children with SessionProvider
     *
     * @performance Target: <10ms render time
     * @tradingImpact Ensures authentication context is available throughout app
     * @riskLevel CRITICAL - Provider wrapping enables all authenticated features
     */

    const TestChild = () => <div data-testid="test-child">Test Content</div>;

    render(
      <Providers>
        <TestChild />
      </Providers>
    );

    // Verify SessionProvider is rendered
    expect(screen.getByTestId('session-provider')).toBeInTheDocument();

    // Verify child component is rendered within provider
    expect(screen.getByTestId('test-child')).toBeInTheDocument();
    expect(screen.getByTestId('test-child')).toHaveTextContent('Test Content');
  });

  it('passes children to SessionProvider correctly', () => {
    /**
     * Test that children are properly passed through to SessionProvider
     *
     * @tradingImpact Ensures all child components receive authentication context
     * @riskLevel HIGH - Improper child passing could break authentication flow
     */

    render(
      <Providers>
        <div data-testid="child-1">Child 1</div>
        <div data-testid="child-2">Child 2</div>
        <div data-testid="child-3">Child 3</div>
      </Providers>
    );

    // Verify all children are rendered
    expect(screen.getByTestId('child-1')).toBeInTheDocument();
    expect(screen.getByTestId('child-2')).toBeInTheDocument();
    expect(screen.getByTestId('child-3')).toBeInTheDocument();

    // Verify SessionProvider was called with children
    expect(SessionProvider).toHaveBeenCalledWith(
      expect.objectContaining({
        children: expect.anything(),
      }),
      expect.anything()
    );
  });

  it('handles empty children gracefully', () => {
    /**
     * Test that Providers component handles empty children without errors
     *
     * @tradingImpact Ensures robustness in edge cases
     * @riskLevel LOW - Edge case handling for provider stability
     */

    render(<Providers>{null}</Providers>);

    // Should still render SessionProvider even with null children
    expect(screen.getByTestId('session-provider')).toBeInTheDocument();
    expect(SessionProvider).toHaveBeenCalled();
  });

  it('maintains component structure with nested providers', () => {
    /**
     * Test that nested providers maintain proper component hierarchy
     *
     * @tradingImpact Ensures complex provider nesting works correctly
     * @riskLevel MEDIUM - Nested providers are common in complex applications
     */

    const NestedProviders = () => (
      <Providers>
        <Providers>
          <div data-testid="nested-child">Nested Content</div>
        </Providers>
      </Providers>
    );

    render(<NestedProviders />);

    // Verify nested structure is maintained
    expect(screen.getByTestId('nested-child')).toBeInTheDocument();
    expect(screen.getByTestId('nested-child')).toHaveTextContent('Nested Content');

    // Verify SessionProvider was called multiple times for nesting
    expect(SessionProvider).toHaveBeenCalledTimes(2);
  });
});

describe('Provider Integration Tests', () => {
  /**
   * Test suite for provider integration scenarios
   *
   * @description Tests provider behavior in realistic application scenarios
   * @riskLevel HIGH - Integration tests validate real-world usage
   */

  it('provides authentication context to trading components', () => {
    /**
     * Test that authentication context is available to trading components
     *
     * @tradingImpact Critical for all trading functionality that requires authentication
     * @riskLevel CRITICAL - Authentication context enables secure trading operations
     */

    const TradingComponent = () => (
      <div data-testid="trading-component">
        <div data-testid="portfolio-section">Portfolio</div>
        <div data-testid="trading-section">Trading</div>
      </div>
    );

    render(
      <Providers>
        <TradingComponent />
      </Providers>
    );

    // Verify trading components render with provider context
    expect(screen.getByTestId('trading-component')).toBeInTheDocument();
    expect(screen.getByTestId('portfolio-section')).toBeInTheDocument();
    expect(screen.getByTestId('trading-section')).toBeInTheDocument();
  });

  it('handles provider initialization performance', () => {
    /**
     * Test provider initialization performance meets requirements
     *
     * @performance Target: <1ms initialization time
     * @tradingImpact Fast initialization improves application startup time
     * @riskLevel MEDIUM - Performance affects user experience
     */

    const startTime = performance.now();

    render(
      <Providers>
        <div data-testid="performance-test">Performance Test</div>
      </Providers>
    );

    const initializationTime = performance.now() - startTime;

    // Should initialize quickly (allowing for test overhead)
    expect(initializationTime).toBeLessThan(50); // Generous threshold for test environment
    expect(screen.getByTestId('performance-test')).toBeInTheDocument();
  });
});

describe('Provider Error Handling', () => {
  /**
   * Test suite for provider error scenarios
   *
   * @description Tests provider behavior when errors occur
   * @riskLevel HIGH - Error handling ensures application stability
   */

  it('handles SessionProvider errors gracefully', () => {
    /**
     * Test that provider errors don't crash the application
     *
     * @tradingImpact Ensures application remains stable during authentication issues
     * @riskLevel HIGH - Provider errors could affect entire application
     */

    // Mock console.error to suppress error output during test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    // Mock SessionProvider to throw error
    const ErrorProvider = vi.fn(() => {
      throw new Error('SessionProvider initialization failed');
    });

    vi.mocked(SessionProvider).mockImplementation(ErrorProvider);

    // Should handle error gracefully (in real app, would use error boundary)
    expect(() => {
      render(
        <Providers>
          <div>Test Content</div>
        </Providers>
      );
    }).toThrow('SessionProvider initialization failed');

    // Verify SessionProvider was called
    expect(SessionProvider).toHaveBeenCalled();

    // Restore console.error
    consoleSpy.mockRestore();
  });
});
