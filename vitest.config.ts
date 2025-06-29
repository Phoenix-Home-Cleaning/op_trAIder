/**
 * @fileoverview Vitest Configuration for TRAIDER V1
 * @module vitest.config
 *
 * @description
 * Comprehensive test configuration for institutional-grade autonomous trading platform.
 * Supports unit testing, integration testing, coverage reporting, and performance
 * benchmarks with parallel execution and advanced reporting.
 *
 * @performance
 * - Latency target: <100ms per test
 * - Throughput: Parallel test execution with worker threads
 * - Memory usage: Optimized for CI/CD environments
 *
 * @risk
 * - Failure impact: CRITICAL - Test failures block deployments
 * - Recovery strategy: Automatic retry for flaky tests
 *
 * @compliance
 * - Audit requirements: Yes - All test results logged and retained
 * - Data retention: 30 days for coverage reports
 *
 * @see {@link docs/testing/vitest-configuration.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    // Test environment configuration
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./tests/setup.ts'],

    // Performance and execution settings
    pool: 'threads',
    poolOptions: {
      threads: {
        maxThreads: 4,
        minThreads: 1,
      },
    },

    // Test discovery and patterns
    include: [
      'app/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'tests/unit/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      'tests/integration/**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
    ],
    exclude: ['node_modules', 'dist', '.next', 'coverage', 'tests/e2e', 'tests/performance'],

    // Coverage configuration for institutional standards
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'json-summary'],
      reportsDirectory: './coverage',

      // Institutional coverage requirements
      thresholds: {
        global: {
          branches: 85,
          functions: 90,
          lines: 90,
          statements: 90,
        },
        // Critical trading components require higher coverage
        './app/lib/trading/**': {
          branches: 95,
          functions: 95,
          lines: 95,
          statements: 95,
        },
        './app/lib/risk/**': {
          branches: 95,
          functions: 95,
          lines: 95,
          statements: 95,
        },
        './app/lib/signals/**': {
          branches: 95,
          functions: 95,
          lines: 95,
          statements: 95,
        },
      },

      // Include/exclude patterns
      include: [
        'app/**/*.{js,ts,jsx,tsx}',
        '!app/**/*.d.ts',
        '!app/**/*.stories.{js,ts,jsx,tsx}',
        '!app/**/*.test.{js,ts,jsx,tsx}',
        '!app/**/*.spec.{js,ts,jsx,tsx}',
      ],
      exclude: [
        'node_modules/',
        'tests/',
        'coverage/',
        '.next/',
        'dist/',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/types.ts',
      ],
    },

    // Reporting configuration
    reporters: ['default', 'json', 'html', ['junit', { outputFile: './test-results.xml' }]],
    outputFile: {
      json: './test-results.json',
      html: './test-results.html',
    },

    // Timeout settings for trading system tests
    testTimeout: 10000, // 10 seconds for complex trading logic
    hookTimeout: 5000, // 5 seconds for setup/teardown

    // Retry configuration for flaky tests
    retry: 1,

    // Watch mode settings
    watch: false, // Disabled in CI

    // Mock configuration
    clearMocks: true,
    restoreMocks: true,

    // Performance monitoring
    logHeapUsage: true,

    // Environment variables for testing
    env: {
      NODE_ENV: 'test',
      TZ: 'UTC',
    },
  },

  // Path resolution for imports
  resolve: {
    alias: {
      '@': resolve(__dirname, './app'),
      '@/components': resolve(__dirname, './app/components'),
      '@/lib': resolve(__dirname, './app/lib'),
      '@/hooks': resolve(__dirname, './app/hooks'),
      '@/types': resolve(__dirname, './app/types'),
      '@/utils': resolve(__dirname, './app/utils'),
      '@/config': resolve(__dirname, './app/config'),
    },
  },

  // Build configuration for test files
  esbuild: {
    target: 'es2022',
  },

  // Define global constants
  define: {
    __TEST__: true,
    __DEV__: false,
    __PROD__: false,
  },
});
