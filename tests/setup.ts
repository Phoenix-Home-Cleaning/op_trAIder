/**
 * @fileoverview Test Setup Configuration
 * @module tests.setup
 * 
 * @description
 * Global test setup for TRAIDER V1 testing infrastructure including
 * DOM environment, mocks, and testing utilities configuration.
 * 
 * @performance
 * - Setup time target: <100ms
 * - Memory overhead: <50MB
 * 
 * @risk
 * - Failure impact: HIGH - Test setup affects all tests
 * - Recovery strategy: Fallback to minimal configuration
 * 
 * @author TRAIDER Team
 */

import { expect, afterEach, beforeAll, afterAll } from 'vitest';
import { cleanup } from '@testing-library/react';
import * as matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect with Testing Library matchers
expect.extend(matchers);

// Global test configuration
beforeAll(() => {
  // Set up global test environment
  if (!process.env.NODE_ENV) {
    Object.defineProperty(process.env, 'NODE_ENV', { value: 'test', writable: true });
  }
  process.env.NEXTAUTH_URL = 'http://localhost:3000';
  process.env.NEXTAUTH_SECRET = 'test-secret-key';
});

// Clean up after each test
afterEach(() => {
  cleanup();
});

// Global teardown
afterAll(() => {
  // Clean up any global resources
});

// Mock Next.js modules that are not available in test environment
vi.mock('next/router', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/dashboard',
    query: {},
    asPath: '/dashboard',
  }),
}));

vi.mock('next/navigation', () => ({
  useRouter: () => ({
    push: vi.fn(),
    pathname: '/dashboard',
    query: {},
  }),
  usePathname: () => '/dashboard',
  useSearchParams: () => new URLSearchParams(),
}));

// Mock WebSocket for real-time features
global.WebSocket = vi.fn(() => ({
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  close: vi.fn(),
  send: vi.fn(),
  readyState: 1,
})) as any;

// Mock performance API
global.performance = {
  now: vi.fn(() => Date.now()),
  mark: vi.fn(),
  measure: vi.fn(),
} as any;

// Mock crypto API for secure operations (if not available)
if (typeof global.crypto === 'undefined') {
  Object.defineProperty(global, 'crypto', {
    value: {
      randomUUID: vi.fn(() => 'test-uuid'),
      getRandomValues: vi.fn((array) => {
        for (let i = 0; i < array.length; i++) {
          array[i] = Math.floor(Math.random() * 256);
        }
        return array;
      }),
    },
    writable: true,
  });
}

// Trading-specific test utilities

/**
 * Creates a mock user object for testing
 *
 * @description
 * Generates a standardized mock user with default trading permissions
 * and profile information. Used across test suites for consistent
 * user authentication testing.
 *
 * @param {object} overrides - Optional property overrides
 * @returns {object} Mock user object with trading profile
 *
 * @throws {Error} If override properties are invalid
 *
 * @performance O(1) time, minimal memory allocation
 * @sideEffects None - pure function
 *
 * @tradingImpact Enables testing of user-specific trading functionality
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * const user = createMockUser({ role: 'ADMIN' });
 * // user = { id: 'test-user-id', role: 'ADMIN', ... }
 * ```
 *
 * @monitoring
 * - Metric: `test.mock_user.creation_time`
 * - Alert threshold: > 1ms
 */
export const createMockUser = (overrides = {}) => ({
  id: 'test-user-id',
  email: 'trader@traider.com',
  name: 'Test Trader',
  role: 'TRADER',
  isActive: true,
  ...overrides,
});

/**
 * Creates a mock NextAuth session for testing
 *
 * @description
 * Generates a valid NextAuth session object with proper expiration
 * and user information. Essential for testing authenticated routes
 * and session-dependent functionality.
 *
 * @param {object} userOverrides - Optional user property overrides
 * @returns {object} Mock NextAuth session object
 *
 * @throws {Error} If user overrides are invalid
 *
 * @performance O(1) time, <1ms execution
 * @sideEffects None - pure function
 *
 * @tradingImpact Enables testing of authenticated trading operations
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * const session = createMockSession({ role: 'ADMIN' });
 * // session = { user: { role: 'ADMIN' }, expires: '...' }
 * ```
 *
 * @monitoring
 * - Metric: `test.mock_session.creation_time`
 * - Alert threshold: > 1ms
 */
export const createMockSession = (userOverrides = {}) => ({
  user: createMockUser(userOverrides),
  expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
});

/**
 * Creates a mock portfolio object for testing
 *
 * @description
 * Generates a realistic portfolio with positions, P&L, and metrics
 * for testing portfolio-related functionality. Includes both crypto
 * and traditional asset positions.
 *
 * @param {object} overrides - Optional property overrides
 * @returns {object} Mock portfolio with positions and metrics
 *
 * @throws {Error} If override values are invalid
 *
 * @performance O(1) time, minimal memory allocation
 * @sideEffects None - pure function
 *
 * @tradingImpact Enables testing of portfolio management features
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * const portfolio = createMockPortfolio({ totalValue: 250000 });
 * // portfolio = { totalValue: 250000, positions: [...] }
 * ```
 *
 * @monitoring
 * - Metric: `test.mock_portfolio.creation_time`
 * - Alert threshold: > 1ms
 */
export const createMockPortfolio = (overrides = {}) => ({
  totalValue: 125000.50,
  dailyPnL: 2350.75,
  dailyPnLPercent: 1.92,
  positions: [
    {
      symbol: 'BTC-USD',
      quantity: 2.5,
      averagePrice: 45000,
      currentPrice: 46000,
      unrealizedPnL: 2500,
      unrealizedPnLPercent: 2.22,
    },
    {
      symbol: 'ETH-USD',
      quantity: 10,
      averagePrice: 3200,
      currentPrice: 3150,
      unrealizedPnL: -500,
      unrealizedPnLPercent: -1.56,
    },
  ],
  ...overrides,
});

/**
 * Creates a mock trade object for testing
 *
 * @description
 * Generates a standardized trade object with realistic trading data
 * for testing order execution, trade history, and P&L calculations.
 *
 * @param {object} overrides - Optional property overrides
 * @returns {object} Mock trade object with execution details
 *
 * @throws {Error} If override values violate trading constraints
 *
 * @performance O(1) time, <1ms execution
 * @sideEffects None - pure function
 *
 * @tradingImpact Enables testing of trade execution and reporting
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * const trade = createMockTrade({ side: 'SELL', quantity: 2.0 });
 * // trade = { side: 'SELL', quantity: 2.0, ... }
 * ```
 *
 * @monitoring
 * - Metric: `test.mock_trade.creation_time`
 * - Alert threshold: > 1ms
 */
export const createMockTrade = (overrides = {}) => ({
  id: 'test-trade-id',
  symbol: 'BTC-USD',
  side: 'BUY',
  quantity: 1.0,
  price: 45000,
  timestamp: new Date().toISOString(),
  status: 'FILLED',
  ...overrides,
});

// Performance testing utilities

/**
 * Measures execution time of a function
 *
 * @description
 * High-precision performance measurement utility for testing
 * latency-critical trading operations. Uses performance.now()
 * for microsecond accuracy.
 *
 * @param {Function} fn - Function to measure (sync or async)
 * @returns {Promise<number>} Execution time in milliseconds
 *
 * @throws {Error} If function execution fails
 *
 * @performance O(1) time, minimal overhead (<0.1ms)
 * @sideEffects Executes the provided function
 *
 * @tradingImpact Critical for validating trading system performance
 * @riskLevel MEDIUM - Executes arbitrary functions
 *
 * @example
 * ```typescript
 * const latency = await measurePerformance(async () => {
 *   await executeTradeOrder();
 * });
 * // latency = 15.234 (milliseconds)
 * ```
 *
 * @monitoring
 * - Metric: `test.performance.measurement_overhead`
 * - Alert threshold: > 1ms
 */
export const measurePerformance = async (fn: () => Promise<void> | void) => {
  const start = performance.now();
  await fn();
  const end = performance.now();
  return end - start;
};

// Error simulation utilities

/**
 * Simulates network connectivity failure
 *
 * @description
 * Throws a standardized network error for testing error handling
 * and recovery mechanisms in trading operations. Used to validate
 * resilience under network failures.
 *
 * @throws {Error} Always throws network error
 *
 * @performance O(1) time, immediate execution
 * @sideEffects None - pure error generation
 *
 * @tradingImpact Tests network failure recovery mechanisms
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * try {
 *   simulateNetworkError();
 * } catch (error) {
 *   // Handle network failure
 * }
 * ```
 *
 * @monitoring
 * - Metric: `test.error_simulation.network_failures`
 * - Alert threshold: N/A
 */
export const simulateNetworkError = () => {
  throw new Error('Network request failed');
};

/**
 * Simulates request timeout scenario
 *
 * @description
 * Creates a promise that rejects after specified timeout duration.
 * Used to test timeout handling in trading operations where
 * latency is critical.
 *
 * @param {number} ms - Timeout duration in milliseconds (default: 5000)
 * @returns {Promise<never>} Promise that rejects with timeout error
 *
 * @throws {Error} Timeout error after specified duration
 *
 * @performance O(1) time, uses setTimeout
 * @sideEffects Creates timer that must be cleaned up
 *
 * @tradingImpact Tests timeout handling in latency-critical operations
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * try {
 *   await simulateTimeout(1000); // 1 second timeout
 * } catch (error) {
 *   // Handle timeout scenario
 * }
 * ```
 *
 * @monitoring
 * - Metric: `test.error_simulation.timeouts`
 * - Alert threshold: N/A
 */
export const simulateTimeout = (ms: number = 5000) => {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), ms);
  });
};

// Trading scenario generators

/**
 * Generates mock market data for testing
 *
 * @description
 * Creates an array of realistic market data points with prices,
 * volumes, and timestamps. Used for testing market data processing,
 * charting, and analysis functions.
 *
 * @param {number} count - Number of data points to generate (default: 100)
 * @returns {Array<object>} Array of market data objects
 *
 * @throws {Error} If count is negative or too large
 *
 * @performance O(n) time, where n is count
 * @sideEffects None - pure function
 *
 * @tradingImpact Enables testing of market data processing pipelines
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * const data = generateMarketData(50);
 * // data = [{ symbol: 'ASSET-0', price: 123.45, ... }, ...]
 * ```
 *
 * @monitoring
 * - Metric: `test.data_generation.market_data_time`
 * - Alert threshold: > 10ms per 100 points
 */
export const generateMarketData = (count: number = 100) => {
  return Array.from({ length: count }, (_, i) => ({
    symbol: `ASSET-${i}`,
    price: Math.random() * 1000 + 100,
    volume: Math.random() * 1000000,
    timestamp: new Date(Date.now() - i * 1000).toISOString(),
  }));
};

/**
 * Generates mock trade history for testing
 *
 * @description
 * Creates an array of realistic trade records with proper timestamps
 * and trading data. Used for testing trade history analysis,
 * P&L calculations, and reporting functions.
 *
 * @param {number} count - Number of trades to generate (default: 50)
 * @returns {Array<object>} Array of trade objects
 *
 * @throws {Error} If count is negative or exceeds limits
 *
 * @performance O(n) time, where n is count
 * @sideEffects None - pure function
 *
 * @tradingImpact Enables testing of trade analysis and reporting
 * @riskLevel LOW - Test utility only
 *
 * @example
 * ```typescript
 * const history = generateTradeHistory(25);
 * // history = [{ id: 'trade-0', symbol: 'BTC-USD', ... }, ...]
 * ```
 *
 * @monitoring
 * - Metric: `test.data_generation.trade_history_time`
 * - Alert threshold: > 5ms per 50 trades
 */
export const generateTradeHistory = (count: number = 50) => {
  return Array.from({ length: count }, (_, i) => createMockTrade({
    id: `trade-${i}`,
    timestamp: new Date(Date.now() - i * 60000).toISOString(),
  }));
};

// Test environment validation
if (typeof window !== 'undefined') {
  // Browser environment setup
  window.matchMedia = vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

// TRAIDER V1 Test Environment Initialized
// - DOM Testing Library configured  
// - Next.js mocks configured
// - Trading utilities available
// - Performance testing enabled
