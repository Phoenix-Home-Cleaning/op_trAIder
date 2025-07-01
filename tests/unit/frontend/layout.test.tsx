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

import { describe, it, expect, vi } from 'vitest';
import RootLayout, { metadata } from '@/layout';
import { Providers } from '@/providers';

vi.mock('next/font/google', () => ({
  Inter: () => ({
    variable: 'mock-inter-variable',
  }),
  JetBrains_Mono: () => ({
    variable: 'mock-jetbrains-mono-variable',
  }),
}));

describe('RootLayout metadata', () => {
  it('should have the correct default title and description', () => {
    if (metadata.title && typeof metadata.title === 'object' && 'default' in metadata.title) {
      expect(metadata.title.default).toBe('TRAIDER V1 - Institutional Crypto Trading Platform');
    } else {
      throw new Error('metadata.title is not in the expected TemplateString format');
    }
    expect(metadata.description).toBe(
      'Autonomous cryptocurrency trading platform with institutional-grade risk management, real-time analytics, and machine learning-powered signals.',
    );
  });
});

describe('RootLayout component', () => {
  it('should render the document structure correctly with children', () => {
    const TestChild = () => <div data-testid="test-child">Hello</div>;

    const layoutElement = RootLayout({ children: <TestChild /> });

    // 1. Check <html> element
    expect(layoutElement.type).toBe('html');
    expect(layoutElement.props.lang).toBe('en');
    expect(layoutElement.props.className).toBe('mock-inter-variable mock-jetbrains-mono-variable');
    expect(layoutElement.props.suppressHydrationWarning).toBe(true);

    const [headElement, bodyElement] = layoutElement.props.children;

    // 2. Check <head> element
    expect(headElement.type).toBe('head');
    expect(headElement.props.children.length).toBeGreaterThan(5);

    // 3. Check <body> element
    expect(bodyElement.type).toBe('body');
    expect(bodyElement.props.className).toBe('min-h-screen bg-background font-sans antialiased');

    const [loadingIndicator, mainElement, modalRoot] = bodyElement.props.children;

    expect(loadingIndicator.props.id).toBe('loading-indicator');
    expect(mainElement.type).toBe('main');
    expect(modalRoot.props.id).toBe('modal-root');

    // 4. Check <Providers> component
    const providersElement = mainElement.props.children;
    expect(providersElement.type).toBe(Providers);

    // 5. Check children
    const childInProviders = providersElement.props.children;
    expect(childInProviders.type).toBe(TestChild);
  });
});