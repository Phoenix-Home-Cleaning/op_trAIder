/**
 * @fileoverview Shared test utilities for TRAIDER V1 test suite
 * @module tests.utils.testHelpers
 * 
 * @description
 * Centralized test utilities to eliminate code duplication and ensure
 * consistent testing patterns across the TRAIDER V1 test suite.
 * 
 * @performance
 * - Helper execution: <1ms per call
 * - Memory usage: <5MB for all utilities
 * 
 * @risk
 * - Failure impact: MEDIUM - Affects all tests using utilities
 * - Recovery strategy: Isolated utility functions with fallbacks
 * 
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { vi, Mock } from 'vitest';
import { render, RenderOptions } from '@testing-library/react';
import React, { ReactElement } from 'react';
import { useSession } from 'next-auth/react';
import { Session } from 'next-auth';

// =============================================================================
// SHARED CONSTANTS
// =============================================================================

export const TEST_CONSTANTS = {
  MOCK_TIMESTAMP: '2024-01-01T12:00:00Z',
  MOCK_USER_ID: 'test-user-123',
  MOCK_SESSION: {
    user: {
      id: 'test-user-123',
      email: 'test@traider.com',
      name: 'Test User',
    },
    expires: '2024-12-31T23:59:59Z',
  },
  TRADING_SYMBOLS: {
    BTC_USD: 'BTC-USD',
    ETH_USD: 'ETH-USD',
  },
} as const;

// =============================================================================
// MOCK CONFIGURATIONS
// =============================================================================

/**
 * Configure Next.js authentication mocks with consistent setup
 */
export const setupAuthMocks = (): {
  mockSignIn: Mock;
  mockSignOut: Mock;
  mockUseSession: Mock;
} => {
  const mockSignIn = vi.fn();
  const mockSignOut = vi.fn();
  const mockUseSession = vi.fn(() => ({
    data: TEST_CONSTANTS.MOCK_SESSION,
    status: 'authenticated',
  }));

  vi.mock('next-auth/react', () => ({
    signIn: mockSignIn,
    signOut: mockSignOut,
    getSession: mockUseSession,
    useSession: mockUseSession,
  }));

  return { mockSignIn, mockSignOut, mockUseSession };
};

/**
 * Configure Next.js router mocks with consistent setup
 */
export const setupRouterMocks = (): {
  mockPush: Mock;
  mockReplace: Mock;
  mockRefresh: Mock;
} => {
  const mockPush = vi.fn();
  const mockReplace = vi.fn();
  const mockRefresh = vi.fn();
  
  vi.mock('next/navigation', () => ({
    useRouter: vi.fn(() => ({
      push: mockPush,
      replace: mockReplace,
      refresh: mockRefresh,
      back: vi.fn(),
      forward: vi.fn(),
      prefetch: vi.fn(),
    })),
    usePathname: vi.fn(() => '/'),
    useSearchParams: vi.fn(() => new URLSearchParams()),
  }));

  vi.mock('next/link', () => ({
    __esModule: true,
    default: ({
      children,
      href,
      ...props
    }: React.PropsWithChildren<{ href: string, }>) => {
      return React.createElement('a', { href, ...props }, children);
    },
  }));

  return { mockPush, mockReplace, mockRefresh };
};

/**
 * Configure comprehensive test environment setup
 */
export const setupTestEnvironment = () => {
  vi.useFakeTimers();
  vi.setSystemTime(new Date(TEST_CONSTANTS.MOCK_TIMESTAMP));
  vi.stubEnv('NODE_ENV', 'test');
  vi.stubEnv('NEXTAUTH_URL', 'http://localhost:3000');
  vi.stubEnv('NEXTAUTH_SECRET', 'test-secret');

  const authMocks = setupAuthMocks();
  const routerMocks = setupRouterMocks();

  return {
    ...authMocks,
    ...routerMocks,
    cleanup: () => {
      vi.restoreAllMocks();
      vi.useRealTimers();
    },
  };
};

// =============================================================================
// TRADING MODEL FACTORIES
// =============================================================================

/**
 * Create mock MarketData instance with realistic values
 */
export const createMockMarketData = (overrides: Record<string, any> = {}) => {
  return {
    timestamp: new Date(TEST_CONSTANTS.MOCK_TIMESTAMP),
    symbol: TEST_CONSTANTS.TRADING_SYMBOLS.BTC_USD,
    price: '50000.00',
    volume: '1.23456789',
    bid: '49999.99',
    ask: '50000.01',
    spread: '0.02',
    trade_count: 5,
    vwap: '50000.00',
    metadata: { exchange: 'coinbase', sequence: 12345 },
    ...overrides,
  };
};

/**
 * Create mock Signal instance with realistic values
 */
export const createMockSignal = (overrides: Record<string, any> = {}) => {
  return {
    symbol: TEST_CONSTANTS.TRADING_SYMBOLS.BTC_USD,
    strategy: 'momentum_v1',
    signal_strength: '0.75',
    confidence: '0.85',
    direction: 'LONG',
    target_price: '52000.00',
    stop_loss: '48000.00',
    take_profit: '55000.00',
    features: { rsi: 65.5, macd: 0.025 },
    executed: false,
    status: 'GENERATED',
    ...overrides,
  };
};

/**
 * Create mock Position instance with realistic values
 */
export const createMockPosition = (overrides: Record<string, any> = {}) => {
  return {
    symbol: TEST_CONSTANTS.TRADING_SYMBOLS.BTC_USD,
    side: 'LONG',
    size: '0.1',
    entry_price: '50000.00',
    current_price: '50500.00',
    unrealized_pnl: '50.00',
    realized_pnl: '0.00',
    status: 'OPEN',
    ...overrides,
  };
};

/**
 * Create mock Trade instance with realistic values
 */
export const createMockTrade = (overrides: Record<string, any> = {}) => {
  return {
    symbol: TEST_CONSTANTS.TRADING_SYMBOLS.BTC_USD,
    side: 'BUY',
    size: '0.1',
    price: '50000.00',
    fee: '5.00',
    status: 'FILLED',
    order_id: 'order-123',
    trade_id: 'trade-456',
    ...overrides,
  };
};

// =============================================================================
// ASSERTION HELPERS
// =============================================================================

/**
 * Assert trading model serialization format
 */
export const assertModelSerialization = (
  model: any,
  expectedFields: string[],
  additionalChecks?: Record<string, any>
) => {
  const serialized = model.to_dict();
  
  expectedFields.forEach(field => {
    if (!(field in serialized)) {
      throw new Error(`Expected field '${field}' not found in serialized model`);
    }
  });

  if (additionalChecks) {
    Object.entries(additionalChecks).forEach(([key, value]) => {
      if (serialized[key] !== value) {
        throw new Error(`Expected ${key} to be ${value}, got ${serialized[key]}`);
      }
    });
  }
};

// =============================================================================
// CUSTOM RENDER UTILITIES
// =============================================================================

/**
 * Custom render function with common providers and setup
 */
export const renderWithProviders = (
  ui: ReactElement,
  options: RenderOptions & { initialSession?: Partial<Session> } = {}
) => {
  const { initialSession, ...renderOptions } = options;

  if (initialSession) {
    vi.mocked(useSession).mockReturnValue({
      data: initialSession as Session,
      status: 'authenticated',
      update: vi.fn(),
    });
  }

  return render(ui, renderOptions);
};

// =============================================================================
// TEST SUITE HELPERS
// =============================================================================

/**
 * Standard test suite setup for consistent test organization
 */
export const createTestSuite = (
  suiteName: string,
  options: {
    setupMocks?: boolean;
    setupTimers?: boolean;
    setupEnv?: boolean;
  } = {}
) => {
  const { setupMocks = true, setupTimers = true, setupEnv = true } = options;

  return {
    beforeEach: () => {
      if (setupMocks) {
        vi.clearAllMocks();
      }
      if (setupTimers) {
        vi.useFakeTimers();
        vi.setSystemTime(new Date(TEST_CONSTANTS.MOCK_TIMESTAMP));
      }
      if (setupEnv) {
        vi.stubEnv('NODE_ENV', 'test');
      }
    },
    afterEach: () => {
      if (setupMocks) {
        vi.restoreAllMocks();
      }
      if (setupTimers) {
        vi.useRealTimers();
      }
    },
    suiteName,
  };
};

// =============================================================================
// EXPORTS
// =============================================================================

export default {
  TEST_CONSTANTS,
  setupAuthMocks,
  setupRouterMocks,
  setupTestEnvironment,
  createMockMarketData,
  createMockSignal,
  createMockPosition,
  createMockTrade,
  assertModelSerialization,
  renderWithProviders,
  createTestSuite,
}; 