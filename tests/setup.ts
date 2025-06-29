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
export const createMockUser = (overrides = {}) => ({
  id: 'test-user-id',
  email: 'trader@traider.com',
  name: 'Test Trader',
  role: 'TRADER',
  isActive: true,
  ...overrides,
});

export const createMockSession = (userOverrides = {}) => ({
  user: createMockUser(userOverrides),
  expires: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
});

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
export const measurePerformance = async (fn: () => Promise<void> | void) => {
  const start = performance.now();
  await fn();
  const end = performance.now();
  return end - start;
};

// Error simulation utilities
export const simulateNetworkError = () => {
  throw new Error('Network request failed');
};

export const simulateTimeout = (ms: number = 5000) => {
  return new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), ms);
  });
};

// Trading scenario generators
export const generateMarketData = (count: number = 100) => {
  return Array.from({ length: count }, (_, i) => ({
    symbol: `ASSET-${i}`,
    price: Math.random() * 1000 + 100,
    volume: Math.random() * 1000000,
    timestamp: new Date(Date.now() - i * 1000).toISOString(),
  }));
};

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
