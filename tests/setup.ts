/**
 * @fileoverview Test Setup Configuration for TRAIDER V1
 * @module tests/setup
 *
 * @description
 * Global test setup and configuration for institutional-grade trading platform tests.
 * Includes environment setup, mocks, utilities, and performance monitoring for
 * comprehensive test coverage of trading components.
 *
 * @performance
 * - Latency target: <10ms setup time per test
 * - Memory usage: Minimal overhead for test isolation
 *
 * @risk
 * - Failure impact: CRITICAL - Test setup failures block all testing
 * - Recovery strategy: Graceful degradation with warnings
 *
 * @compliance
 * - Audit requirements: Yes - Test environment logged
 * - Data retention: Test logs retained for 30 days
 *
 * @see {@link docs/testing/test-setup.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { vi, beforeEach, afterEach, beforeAll, afterAll } from 'vitest';

// =============================================================================
// GLOBAL TEST ENVIRONMENT SETUP
// =============================================================================

/**
 * Configure global test environment
 */
beforeAll(() => {
  // Set timezone to UTC for consistent test results
  process.env.TZ = 'UTC';

  // Configure test environment variables
  Object.defineProperty(process.env, 'NODE_ENV', { value: 'test', writable: true });
  Object.defineProperty(process.env, 'CI', { value: 'true', writable: true });

  // Mock console methods to reduce test noise
  if (!process.env.DEBUG_TESTS) {
    vi.spyOn(console, 'log').mockImplementation(() => {});
    vi.spyOn(console, 'info').mockImplementation(() => {});
    vi.spyOn(console, 'debug').mockImplementation(() => {});
  }

  // Keep console.warn and console.error for important messages
  const originalWarn = console.warn;
  const originalError = console.error;

  vi.spyOn(console, 'warn').mockImplementation((...args) => {
    if (process.env.DEBUG_TESTS) {
      originalWarn(...args);
    }
  });

  vi.spyOn(console, 'error').mockImplementation((...args) => {
    if (process.env.DEBUG_TESTS) {
      originalError(...args);
    }
  });
});

/**
 * Cleanup after all tests
 */
afterAll(() => {
  vi.restoreAllMocks();
});

// =============================================================================
// PER-TEST SETUP AND CLEANUP
// =============================================================================

/**
 * Setup before each test
 */
beforeEach(() => {
  // Reset all mocks to ensure test isolation
  vi.clearAllMocks();

  // Reset timers for consistent time-based testing
  vi.useFakeTimers();
  vi.setSystemTime(new Date('2024-01-01T00:00:00.000Z'));
});

/**
 * Cleanup after each test
 */
afterEach(() => {
  // Restore real timers
  vi.useRealTimers();

  // Clear all mocks
  vi.clearAllMocks();
});

// =============================================================================
// TRADING SYSTEM MOCKS
// =============================================================================

/**
 * Mock market data for consistent testing
 */
export const mockMarketData = {
  'BTC-USD': {
    price: 45000.0,
    volume: 1234.5678,
    timestamp: '2024-01-01T00:00:00.000Z',
    bid: 44999.5,
    ask: 45000.5,
    spread: 1.0,
  },
  'ETH-USD': {
    price: 3000.0,
    volume: 5678.1234,
    timestamp: '2024-01-01T00:00:00.000Z',
    bid: 2999.75,
    ask: 3000.25,
    spread: 0.5,
  },
};

/**
 * Mock trading signals for testing
 */
export const mockTradingSignals = {
  momentum: {
    symbol: 'BTC-USD',
    signal: 0.75,
    confidence: 0.85,
    timestamp: '2024-01-01T00:00:00.000Z',
    strategy: 'momentum_v2',
  },
  meanReversion: {
    symbol: 'ETH-USD',
    signal: -0.6,
    confidence: 0.7,
    timestamp: '2024-01-01T00:00:00.000Z',
    strategy: 'mean_reversion',
  },
};

/**
 * Mock portfolio positions for testing
 */
export const mockPositions = {
  'BTC-USD': {
    symbol: 'BTC-USD',
    quantity: 0.1,
    avgCost: 44500.0,
    unrealizedPnL: 50.0,
    realizedPnL: 125.5,
    lastUpdated: '2024-01-01T00:00:00.000Z',
  },
  'ETH-USD': {
    symbol: 'ETH-USD',
    quantity: 2.0,
    avgCost: 2950.0,
    unrealizedPnL: 100.0,
    realizedPnL: -25.75,
    lastUpdated: '2024-01-01T00:00:00.000Z',
  },
};

// =============================================================================
// API MOCKS
// =============================================================================

/**
 * Mock fetch for API calls
 */
global.fetch = vi.fn();

/**
 * Mock WebSocket for real-time connections
 */
interface MockWebSocket {
  readyState: number;
  send: ReturnType<typeof vi.fn>;
  close: ReturnType<typeof vi.fn>;
  addEventListener: ReturnType<typeof vi.fn>;
  removeEventListener: ReturnType<typeof vi.fn>;
  dispatchEvent: ReturnType<typeof vi.fn>;
}

(global as { WebSocket: unknown }).WebSocket = vi.fn().mockImplementation(
  (): MockWebSocket => ({
    readyState: 1, // OPEN
    send: vi.fn(),
    close: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })
);

// =============================================================================
// PERFORMANCE MONITORING UTILITIES
// =============================================================================

/**
 * Performance measurement utility for tests
 */
export class TestPerformanceMonitor {
  private startTime: number = 0;
  private endTime: number = 0;

  start(): void {
    this.startTime = performance.now();
  }

  end(): number {
    this.endTime = performance.now();
    return this.endTime - this.startTime;
  }

  assertLatency(maxMs: number, operation: string): void {
    const duration = this.end();
    if (duration > maxMs) {
      throw new Error(
        `Performance assertion failed: ${operation} took ${duration.toFixed(2)}ms, expected ≤${maxMs}ms`
      );
    }
  }
}

/**
 * Create performance monitor instance
 */
export const createPerformanceMonitor = (): TestPerformanceMonitor => {
  return new TestPerformanceMonitor();
};

// =============================================================================
// TEST UTILITIES
// =============================================================================

/**
 * Wait for a specified number of milliseconds
 */
export const wait = (ms: number): Promise<void> => {
  return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Wait for a condition to be true with timeout
 */
export const waitFor = async (
  condition: () => boolean | Promise<boolean>,
  timeoutMs: number = 5000,
  intervalMs: number = 100
): Promise<void> => {
  const start = Date.now();

  while (Date.now() - start < timeoutMs) {
    if (await condition()) {
      return;
    }
    await wait(intervalMs);
  }

  throw new Error(`Condition not met within ${timeoutMs}ms`);
};

/**
 * Generate random market data for testing
 */
export const generateRandomMarketData = (symbol: string, basePrice: number) => {
  const variation = (Math.random() - 0.5) * 0.02; // ±1% variation
  const price = basePrice * (1 + variation);

  return {
    symbol,
    price: Number(price.toFixed(2)),
    volume: Math.random() * 10000,
    timestamp: new Date().toISOString(),
    bid: Number((price * 0.9995).toFixed(2)),
    ask: Number((price * 1.0005).toFixed(2)),
    spread: Number((price * 0.001).toFixed(2)),
  };
};

/**
 * Generate random trading signal for testing
 */
export const generateRandomSignal = (symbol: string, strategy: string) => {
  return {
    symbol,
    signal: (Math.random() - 0.5) * 2, // -1 to 1
    confidence: Math.random() * 0.5 + 0.5, // 0.5 to 1
    timestamp: new Date().toISOString(),
    strategy,
  };
};

// =============================================================================
// ERROR HANDLING UTILITIES
// =============================================================================

/**
 * Expect function to throw specific error
 */
export const expectToThrow = async (
  fn: () => Promise<unknown> | unknown,
  expectedError?: string | RegExp
): Promise<void> => {
  try {
    await fn();
    throw new Error('Expected function to throw, but it did not');
  } catch (error) {
    if (expectedError) {
      const message = error instanceof Error ? error.message : String(error);
      if (typeof expectedError === 'string') {
        if (!message.includes(expectedError)) {
          throw new Error(`Expected error to contain "${expectedError}", got "${message}"`);
        }
      } else if (!expectedError.test(message)) {
        throw new Error(`Expected error to match ${expectedError}, got "${message}"`);
      }
    }
  }
};

// =============================================================================
// TRADING SYSTEM TEST HELPERS
// =============================================================================

/**
 * Simulate market data stream for testing
 */
interface MarketDataPoint {
  symbol: string;
  price: number;
  volume: number;
  timestamp: string;
  bid: number;
  ask: number;
  spread: number;
}

export const simulateMarketDataStream = (
  symbols: string[],
  durationMs: number = 1000,
  intervalMs: number = 100
) => {
  const data: MarketDataPoint[] = [];
  const basePrices: Record<string, number> = {
    'BTC-USD': 45000,
    'ETH-USD': 3000,
    'SOL-USD': 100,
  };

  return new Promise<MarketDataPoint[]>((resolve) => {
    const interval = setInterval(() => {
      symbols.forEach((symbol) => {
        const basePrice = basePrices[symbol] || 1000;
        data.push(generateRandomMarketData(symbol, basePrice));
      });
    }, intervalMs);

    setTimeout(() => {
      clearInterval(interval);
      resolve(data);
    }, durationMs);
  });
};

/**
 * Mock database connection for testing
 */
export const mockDatabaseConnection = {
  query: vi.fn().mockResolvedValue({ rows: [], rowCount: 0 }),
  connect: vi.fn().mockResolvedValue(undefined),
  end: vi.fn().mockResolvedValue(undefined),
  release: vi.fn().mockResolvedValue(undefined),
};

// =============================================================================
// EXPORT TEST CONFIGURATION
// =============================================================================

export const testConfig = {
  timeout: {
    unit: 5000, // 5 seconds for unit tests
    integration: 15000, // 15 seconds for integration tests
    performance: 60000, // 60 seconds for performance tests
  },
  performance: {
    maxLatency: {
      signalGeneration: 100, // 100ms max for signal generation
      riskCalculation: 50, // 50ms max for risk calculations
      orderExecution: 500, // 500ms max for order execution
    },
  },
  mock: {
    marketData: mockMarketData,
    signals: mockTradingSignals,
    positions: mockPositions,
    database: mockDatabaseConnection,
  },
};

// Test setup completion logged via test framework
