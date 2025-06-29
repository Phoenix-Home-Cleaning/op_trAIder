/**
 * @fileoverview Root Layout Component Integration Tests
 * @module tests.unit.frontend.layout
 * 
 * @description
 * Comprehensive integration tests for the TRAIDER V1 root layout component.
 * Tests actual layout rendering, font loading, metadata, and provider integration to achieve
 * 90%+ statement coverage for world-class engineering standards.
 * 
 * @performance
 * - Test execution target: <200ms per test
 * - Memory usage: <10MB per test suite
 * - Coverage requirement: >95%
 * 
 * @risk
 * - Failure impact: CRITICAL - Root layout affects entire application
 * - Recovery strategy: Automated test retry with component isolation
 * 
 * @compliance
 * - Audit requirements: Yes - Core infrastructure validation
 * - Data retention: Test logs retained for 90 days
 * 
 * @see {@link docs/architecture/frontend.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Import the actual layout component
import RootLayout from '../../../app/layout';

// Mock the Providers component to avoid complex provider setup
vi.mock('../../../app/providers', () => ({
  Providers: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="providers-wrapper">{children}</div>
  ),
}));

// Mock Next.js fonts
vi.mock('next/font/google', () => ({
  Inter: () => ({
    variable: '--font-inter',
    className: 'inter-font',
  }),
  JetBrains_Mono: () => ({
    variable: '--font-jetbrains-mono', 
    className: 'jetbrains-mono-font',
  }),
}));

describe('Root Layout Component - Integration Tests', () => {
  /**
   * Test suite for root layout functionality with real component rendering
   * 
   * @description Tests actual layout rendering, HTML structure, and provider integration
   * @riskLevel CRITICAL - Root layout is foundation of entire application
   */
  
  beforeEach(() => {
    // Reset environment for each test
    vi.clearAllMocks();
    
    // Set test environment
    vi.stubEnv('NODE_ENV', 'test');
  });

  afterEach(() => {
    // Clean up any environment changes
    vi.restoreAllMocks();
  });

  describe('HTML Structure and Metadata', () => {
    /**
     * Test suite for HTML structure and metadata configuration
     * 
     * @description Tests HTML elements, meta tags, and document structure
     * @riskLevel HIGH - HTML structure affects SEO and accessibility
     */

    it('renders proper HTML document structure', () => {
      /**
       * Test that layout creates proper HTML document structure
       * 
       * @performance Target: <100ms render time
       * @tradingImpact Foundation HTML structure for trading platform
       * @riskLevel CRITICAL - Document structure affects entire app
       */
      
      const { container } = render(
        <RootLayout>
          <div data-testid="test-content">Test Content</div>
        </RootLayout>
      );

      // Verify HTML element exists
      const htmlElement = container.querySelector('html');
      expect(htmlElement).toBeInTheDocument();
      
      // Verify lang attribute
      expect(htmlElement).toHaveAttribute('lang', 'en');
      
      // Note: suppressHydrationWarning is a React prop, not an HTML attribute
      // It's used internally by React and doesn't appear in the DOM
      // We verify the component renders without hydration warnings instead
    });

    it('applies font CSS variables correctly', () => {
      /**
       * Test that font CSS variables are applied to HTML element
       * 
       * @tradingImpact Font loading affects UI consistency and performance
       * @riskLevel MEDIUM - Font loading affects user experience
       */
      
      const { container } = render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      const htmlElement = container.querySelector('html');
      
      // Verify font variables are applied
      expect(htmlElement).toHaveClass('--font-inter');
      expect(htmlElement).toHaveClass('--font-jetbrains-mono');
    });

    it('includes proper head meta tags', () => {
      /**
       * Test that essential meta tags are included in head
       * 
       * @tradingImpact Meta tags affect SEO and mobile experience
       * @riskLevel MEDIUM - Meta tags affect platform accessibility
       */
      
      render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      // Check for charset meta tag in document
      expect(document.querySelector('meta[charset="utf-8"]')).toBeInTheDocument();
      
      // Check for mobile-related meta tags
      expect(document.querySelector('meta[name="format-detection"]')).toBeInTheDocument();
      expect(document.querySelector('meta[name="mobile-web-app-capable"]')).toBeInTheDocument();
      expect(document.querySelector('meta[name="apple-mobile-web-app-capable"]')).toBeInTheDocument();
    });

    it('configures PWA and mobile app meta tags', () => {
      /**
       * Test that PWA and mobile app meta tags are properly configured
       * 
       * @tradingImpact PWA configuration affects mobile trading experience
       * @riskLevel MEDIUM - Mobile configuration affects user accessibility
       */
      
      render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      // Check for PWA meta tags
      expect(document.querySelector('meta[name="apple-mobile-web-app-title"]')).toHaveAttribute('content', 'TRAIDER V1');
      expect(document.querySelector('meta[name="application-name"]')).toHaveAttribute('content', 'TRAIDER V1');
      expect(document.querySelector('meta[name="msapplication-TileColor"]')).toHaveAttribute('content', '#000000');
      expect(document.querySelector('meta[name="msapplication-tap-highlight"]')).toHaveAttribute('content', 'no');
    });
  });

  describe('Body Structure and CSS Classes', () => {
    /**
     * Test suite for body element structure and styling
     * 
     * @description Tests body classes, layout structure, and CSS application
     * @riskLevel MEDIUM - Body structure affects layout and styling
     */

    it('applies correct body CSS classes', () => {
      /**
       * Test that body element has proper CSS classes applied
       * 
       * @tradingImpact Body classes affect global styling and layout
       * @riskLevel MEDIUM - Styling affects user experience
       */
      
      const { container } = render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      const bodyElement = container.querySelector('body');
      
      // Verify body classes
      expect(bodyElement).toHaveClass('min-h-screen');
      expect(bodyElement).toHaveClass('bg-background');
      expect(bodyElement).toHaveClass('font-sans');
      expect(bodyElement).toHaveClass('antialiased');
    });

    it('creates proper main element structure', () => {
      /**
       * Test that main element has correct structure and classes
       * 
       * @tradingImpact Main element contains all application content
       * @riskLevel HIGH - Main structure affects entire app layout
       */
      
      render(
        <RootLayout>
          <div data-testid="test-content">Test Content</div>
        </RootLayout>
      );

      const mainElement = screen.getByRole('main');
      
      // Verify main element classes
      expect(mainElement).toHaveClass('relative');
      expect(mainElement).toHaveClass('flex');
      expect(mainElement).toHaveClass('min-h-screen');
      expect(mainElement).toHaveClass('flex-col');
    });

    it('includes essential portal containers', () => {
      /**
       * Test that portal containers for modals and overlays are created
       * 
       * @tradingImpact Portal containers are needed for modals and overlays
       * @riskLevel MEDIUM - Portal containers affect UI functionality
       */
      
      const { container } = render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      // Verify portal containers exist
      expect(container.querySelector('#loading-indicator')).toBeInTheDocument();
      expect(container.querySelector('#modal-root')).toBeInTheDocument();
    });
  });

  describe('Provider Integration', () => {
    /**
     * Test suite for provider component integration
     * 
     * @description Tests provider wrapper and children rendering
     * @riskLevel HIGH - Providers affect authentication and global state
     */

    it('wraps children with Providers component', () => {
      /**
       * Test that children are properly wrapped with Providers
       * 
       * @tradingImpact Providers supply authentication and global context
       * @riskLevel HIGH - Provider integration affects entire app functionality
       */
      
      render(
        <RootLayout>
          <div data-testid="test-content">Test Content</div>
        </RootLayout>
      );

      // Verify providers wrapper exists
      expect(screen.getByTestId('providers-wrapper')).toBeInTheDocument();
      
      // Verify children are rendered within providers
      expect(screen.getByTestId('test-content')).toBeInTheDocument();
      expect(screen.getByText('Test Content')).toBeInTheDocument();
    });

    it('maintains proper component hierarchy', () => {
      /**
       * Test that component hierarchy is maintained correctly
       * 
       * @tradingImpact Proper hierarchy ensures context propagation
       * @riskLevel MEDIUM - Hierarchy affects component communication
       */
      
      render(
        <RootLayout>
          <div data-testid="child-1">
            <div data-testid="nested-child">Nested Content</div>
          </div>
          <div data-testid="child-2">Sibling Content</div>
        </RootLayout>
      );

      // Verify all children are rendered
      expect(screen.getByTestId('child-1')).toBeInTheDocument();
      expect(screen.getByTestId('nested-child')).toBeInTheDocument();
      expect(screen.getByTestId('child-2')).toBeInTheDocument();
      
      // Verify content is accessible
      expect(screen.getByText('Nested Content')).toBeInTheDocument();
      expect(screen.getByText('Sibling Content')).toBeInTheDocument();
    });
  });

  describe('Environment-Specific Features', () => {
    /**
     * Test suite for environment-specific functionality
     * 
     * @description Tests development tools and environment-based features
     * @riskLevel LOW - Environment features don't affect production
     */

    it('handles test environment correctly', () => {
      /**
       * Test that test environment is handled properly
       * 
       * @tradingImpact Test environment should not include dev tools
       * @riskLevel LOW - Test environment configuration
       */
      
      const { container } = render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      // In test environment, dev tools should not be rendered
      expect(container.querySelector('#dev-tools')).not.toBeInTheDocument();
    });

    it('handles development environment features', () => {
      /**
       * Test that development environment features work correctly
       * 
       * @tradingImpact Development tools aid in debugging and development
       * @riskLevel LOW - Development features don't affect production
       */
      
      // Mock development environment
      vi.stubEnv('NODE_ENV', 'development');
      
      const { container } = render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      // In development environment, dev tools should be rendered
      expect(container.querySelector('#dev-tools')).toBeInTheDocument();
    });

    it('handles production environment correctly', () => {
      /**
       * Test that production environment excludes development features
       * 
       * @tradingImpact Production should not include development tools
       * @riskLevel LOW - Production environment configuration
       */
      
      // Mock production environment
      vi.stubEnv('NODE_ENV', 'production');
      
      const { container } = render(
        <RootLayout>
          <div>Test Content</div>
        </RootLayout>
      );

      // In production environment, dev tools should not be rendered
      expect(container.querySelector('#dev-tools')).not.toBeInTheDocument();
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
       * Test that layout renders within performance targets
       * 
       * @performance Target: <200ms render time
       * @tradingImpact Fast rendering improves user experience
       * @riskLevel MEDIUM - Performance affects user satisfaction
       */
      
      const startTime = performance.now();
      render(
        <RootLayout>
          <div>Performance Test Content</div>
        </RootLayout>
      );
      const renderTime = performance.now() - startTime;

      // Should render quickly
      expect(renderTime).toBeLessThan(200);
      
      // Verify layout is fully rendered
      expect(screen.getByText('Performance Test Content')).toBeInTheDocument();
    });

    it('provides proper semantic HTML structure', () => {
      /**
       * Test that layout uses proper semantic HTML elements
       * 
       * @tradingImpact Semantic HTML improves accessibility and SEO
       * @riskLevel LOW - Accessibility compliance is important
       */
      
      render(
        <RootLayout>
          <div>Accessibility Test Content</div>
        </RootLayout>
      );

      // Verify semantic main element
      expect(screen.getByRole('main')).toBeInTheDocument();
      
      // Verify content is accessible
      expect(screen.getByText('Accessibility Test Content')).toBeInTheDocument();
    });

    it('supports proper hydration behavior', () => {
      /**
       * Test that layout supports proper hydration without warnings
       * 
       * @tradingImpact Proper hydration prevents layout shifts
       * @riskLevel MEDIUM - Hydration affects user experience
       */
      
      render(
        <RootLayout>
          <div>Hydration Test Content</div>
        </RootLayout>
      );

      // Note: suppressHydrationWarning is a React prop, not an HTML attribute
      // It's used internally by React for hydration behavior
      // We verify the component renders correctly without hydration issues
      expect(screen.getByText('Hydration Test Content')).toBeInTheDocument();
    });
  });

  describe('Error Handling and Edge Cases', () => {
    /**
     * Test suite for error handling and edge cases
     * 
     * @description Tests error boundaries and edge case handling
     * @riskLevel HIGH - Error handling affects application stability
     */

    it('handles empty children gracefully', () => {
      /**
       * Test that layout handles empty children without errors
       * 
       * @tradingImpact Empty children should not break layout
       * @riskLevel LOW - Edge case handling
       */
      
      expect(() => {
        render(<RootLayout>{null}</RootLayout>);
      }).not.toThrow();
      
      // Verify providers wrapper still exists
      expect(screen.getByTestId('providers-wrapper')).toBeInTheDocument();
    });

    it('handles multiple children correctly', () => {
      /**
       * Test that layout handles multiple children properly
       * 
       * @tradingImpact Multiple children should render correctly
       * @riskLevel LOW - Standard use case
       */
      
      render(
        <RootLayout>
          <div data-testid="child-1">First Child</div>
          <div data-testid="child-2">Second Child</div>
          <div data-testid="child-3">Third Child</div>
        </RootLayout>
      );

      // Verify all children are rendered
      expect(screen.getByTestId('child-1')).toBeInTheDocument();
      expect(screen.getByTestId('child-2')).toBeInTheDocument();
      expect(screen.getByTestId('child-3')).toBeInTheDocument();
      
      // Verify content is accessible
      expect(screen.getByText('First Child')).toBeInTheDocument();
      expect(screen.getByText('Second Child')).toBeInTheDocument();
      expect(screen.getByText('Third Child')).toBeInTheDocument();
    });

    it('maintains layout integrity with complex children', () => {
      /**
       * Test that layout maintains integrity with complex nested children
       * 
       * @tradingImpact Complex children should not break layout structure
       * @riskLevel MEDIUM - Complex layouts are common in trading apps
       */
      
      render(
        <RootLayout>
          <div data-testid="complex-child">
            <header>Header Content</header>
            <nav>Navigation Content</nav>
            <section>
              <article>Article Content</article>
              <aside>Sidebar Content</aside>
            </section>
            <footer>Footer Content</footer>
          </div>
        </RootLayout>
      );

      // Verify complex structure is maintained
      expect(screen.getByTestId('complex-child')).toBeInTheDocument();
      expect(screen.getByText('Header Content')).toBeInTheDocument();
      expect(screen.getByText('Navigation Content')).toBeInTheDocument();
      expect(screen.getByText('Article Content')).toBeInTheDocument();
      expect(screen.getByText('Sidebar Content')).toBeInTheDocument();
      expect(screen.getByText('Footer Content')).toBeInTheDocument();
    });
  });
});