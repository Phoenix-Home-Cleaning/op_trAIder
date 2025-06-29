/**
 * @fileoverview Performance Testing Configuration for TRAIDER V1
 * @module vitest.performance.config
 *
 * @description
 * Specialized configuration for performance and benchmark testing of trading components.
 * Focuses on latency measurements, throughput testing, and resource utilization
 * monitoring for institutional-grade performance requirements.
 *
 * @performance
 * - Target: P95 ≤ 500ms signal-to-order execution
 * - Throughput: 1000+ operations per second
 * - Memory: Stable memory usage under load
 *
 * @risk
 * - Failure impact: HIGH - Performance regression blocks deployment
 * - Recovery strategy: Automatic performance baseline comparison
 *
 * @compliance
 * - Audit requirements: Yes - Performance metrics logged
 * - Data retention: 90 days for benchmark history
 *
 * @see {@link docs/testing/performance-testing.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { defineConfig } from 'vitest/config';
import { resolve } from 'path';

export default defineConfig({
  test: {
    // Performance test environment
    environment: 'node',
    globals: true,

    // Performance-specific settings
    pool: 'forks', // Use forks for isolated performance tests
    poolOptions: {
      forks: {
        maxForks: 1, // Single fork for consistent performance measurement
        minForks: 1,
      },
    },

    // Test discovery for performance tests only
    include: [
      'tests/performance/**/*.{test,spec}.{js,ts}',
      'tests/benchmarks/**/*.{test,spec}.{js,ts}',
    ],
    exclude: ['node_modules', 'dist', '.next', 'coverage'],

    // Extended timeouts for performance tests
    testTimeout: 60000, // 60 seconds for complex benchmarks
    hookTimeout: 10000,

    // No retries for performance tests (consistent measurements)
    retry: 0,

    // Disable coverage for performance tests
    coverage: {
      enabled: false,
    },

    // Performance-focused reporting
    reporters: ['verbose'],
    outputFile: {
      json: './performance-results.json',
      junit: './performance-results.xml',
    },

    // Environment for performance testing
    env: {
      NODE_ENV: 'performance',
      TZ: 'UTC',
      // Disable logging to reduce noise in performance measurements
      LOG_LEVEL: 'error',
    },

    // Benchmark configuration
    benchmark: {
      include: ['tests/benchmarks/**/*.{bench,benchmark}.{js,ts}'],
      exclude: ['node_modules/**', 'dist/**'],
    },
  },

  // Path resolution
  resolve: {
    alias: {
      '@': resolve(__dirname, './app'),
      '@/lib': resolve(__dirname, './app/lib'),
      '@/utils': resolve(__dirname, './app/utils'),
      '@/config': resolve(__dirname, './app/config'),
    },
  },

  // Optimized build for performance testing
  esbuild: {
    target: 'es2022',
    minify: false, // Disable minification for accurate profiling
    sourcemap: true,
  },

  // Define constants for performance tests
  define: {
    __PERFORMANCE_TEST__: true,
    __TEST__: true,
    __DEV__: false,
    __PROD__: false,
  },
});
