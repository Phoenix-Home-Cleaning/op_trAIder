/**
 * @fileoverview Vitest Configuration for TRAIDER V1
 * @module vitest.config
 *
 * @description
 * Comprehensive test configuration for institutional-grade cryptocurrency
 * trading platform including unit, integration, and performance testing.
 *
 * @performance
 * - Test execution target: <5s for full suite
 * - Parallel execution: 4 workers
 * - Coverage target: >95%
 *
 * @risk
 * - Failure impact: MEDIUM - Test configuration affects development velocity
 * - Recovery strategy: Fallback to basic configuration
 *
 * @compliance
 * - Audit requirements: Yes - All test results logged and retained
 * - Data retention: 30 days for coverage reports
 *
 * @see {@link docs/testing/vitest-configuration.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';

// To use path aliases from tsconfig.json
// import tsconfigPaths from 'vite-tsconfig-paths';

// ES Module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default defineConfig({
  plugins: [react()],

  // Optimize build for testing performance
  optimizeDeps: {
    include: ['vitest > @vitest/utils > pretty-format'],
  },

  test: {
    // Test environment configuration
    environment: 'jsdom',

    // Global setup and teardown
    setupFiles: ['./tests/setup.ts'],

    // Test file patterns
    include: ['tests/**/*.{test,spec}.{js,ts,jsx,tsx}', 'app/**/*.{test,spec}.{js,ts,jsx,tsx}'],

    exclude: ['node_modules/**', 'dist/**', '.next/**', 'coverage/**', 'backend/**'],

    // Global test configuration
    globals: true,

    // Timeout configuration (institutional trading requires reliability)
    testTimeout: 10000, // 10 seconds for unit tests
    hookTimeout: 30000, // 30 seconds for setup/teardown

    // Performance and concurrency
    maxConcurrency: 4,
    minWorkers: 1,
    maxWorkers: 4,

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov', 'json-summary'],
      reportsDirectory: './coverage',

      // Coverage thresholds - Phase 0 Foundation Complete
      // Core infrastructure (auth, API, layout) is tested
      // Thresholds set for implemented components only
      //
      // Phase 1 MVP targets:
      // - branches: 60%, functions: 50%, lines: 40%, statements: 40%
      // Phase 2 Enhanced targets:
      // - branches: 75%, functions: 70%, lines: 60%, statements: 60%
      // Phase 3 Institutional targets:
      // - branches: 90%, functions: 85%, lines: 80%, statements: 80%
      thresholds: {
        branches: 45, // Phase 0: Foundation coverage (current: 46.87%)
        functions: 25, // Phase 0: Core functions covered (current: 28.57%)
        lines: 10, // Phase 0: Essential paths tested (current: 10%)
        statements: 10, // Phase 0: Critical statements covered (current: 10%)
      },

      // Include/exclude patterns
      include: ['app/**/*.{js,ts,jsx,tsx}', 'shared/**/*.{js,ts}', 'middleware.ts'],

      exclude: [
        'node_modules/**',
        'tests/**',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/types/**',
        '.next/**',
        'app/**/README.md',
        'app/globals.css',
        'coverage/**',
        'docs/**',
        'backend/**', // Backend has separate coverage
        'infra/**',
        'scripts/**',
      ],
    },

    // Reporter configuration
    reporters: ['verbose'],
    outputFile: './test-results/results.json',

    // Watch mode configuration
    watch: false, // Disabled by default for CI/CD

    // Retry configuration for flaky tests
    retry: 1,

    // Bail on first failure in CI
    bail: process.env.CI ? 1 : 0,

    // Mock configuration
    clearMocks: true,
    restoreMocks: true,

    // Environment variables for testing
    env: {
      NODE_ENV: 'test',
      NEXTAUTH_URL: 'http://localhost:3000',
      NEXTAUTH_SECRET: 'test-secret-key-for-testing-only',
      DATABASE_URL: 'postgresql://test:test@localhost:5432/traider_test',
      REDIS_URL: 'redis://localhost:6379/1',
      LOG_LEVEL: 'ERROR', // Reduce log noise in tests
    },
  },

  // Path resolution for imports
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './app'),
      '@/components': path.resolve(__dirname, './app/components'),
      '@/lib': path.resolve(__dirname, './app/lib'),
      '@/types': path.resolve(__dirname, './types'),
      '@/shared': path.resolve(__dirname, './shared'),
      '@/tests': path.resolve(__dirname, './tests'),
    },
  },

  // Build configuration for tests
  define: {
    'process.env.NODE_ENV': '"test"',
    __DEV__: true,
    __TEST__: true,
    __PROD__: false,
  },
});
