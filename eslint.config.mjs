/**
 * @fileoverview ESLint 9 Flat Configuration for TRAIDER V1
 * @module eslint.config.mjs
 *
 * @description
 * Modern ESLint flat configuration for institutional-grade cryptocurrency
 * trading platform. Supports Next.js 15, React 19, TypeScript, and 
 * institutional coding standards.
 *
 * @performance
 * - Linting target: <2s for full codebase
 * - Parallel execution: Enabled
 * - Cache: Enabled for performance
 *
 * @risk
 * - Failure impact: MEDIUM - Affects code quality and security
 * - Recovery strategy: Fallback to basic rules
 *
 * @compliance
 * - Audit requirements: Yes - All linting results logged
 * - Data retention: 30 days for reports
 *
 * @see {@link docs/development/eslint-configuration.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { FlatCompat } from '@eslint/eslintrc';
import js from '@eslint/js';
import path from 'path';
import { fileURLToPath } from 'url';

// Get current directory for flat config compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Initialize compatibility layer for legacy configs
const compat = new FlatCompat({
  baseDirectory: __dirname,
  recommendedConfig: js.configs.recommended,
  allConfig: js.configs.all,
});

/** @type {import('eslint').Linter.Config[]} */
export default [
  // Base JavaScript recommended rules
  js.configs.recommended,
  
  // Next.js and React configuration using compatibility layer
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  
  // Global configuration
  {
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        // Node.js globals
        process: 'readonly',
        Buffer: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        
        // Browser globals
        window: 'readonly',
        document: 'readonly',
        console: 'readonly',
        
        // Testing globals
        describe: 'readonly',
        it: 'readonly',
        expect: 'readonly',
        beforeEach: 'readonly',
        afterEach: 'readonly',
        beforeAll: 'readonly',
        afterAll: 'readonly',
        vi: 'readonly',
        vitest: 'readonly',
      },
    },
    
    rules: {
      // Trading-specific rules for institutional grade code
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'no-debugger': 'error',
      'no-alert': 'error',
      
      // Security rules for financial applications
      'no-eval': 'error',
      'no-implied-eval': 'error',
      'no-new-func': 'error',
      'no-script-url': 'error',
      
      // Performance rules
      'prefer-const': 'error',
      'no-var': 'error',
      'object-shorthand': 'error',
      
      // Code quality rules
      'eqeqeq': ['error', 'always'],
      'curly': ['error', 'all'],
      'no-unused-vars': ['error', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        ignoreRestSiblings: true 
      }],
      
      // TypeScript specific overrides
      '@typescript-eslint/no-unused-vars': ['error', { 
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        ignoreRestSiblings: true 
      }],
      '@typescript-eslint/explicit-function-return-type': 'off',
      '@typescript-eslint/explicit-module-boundary-types': 'off',
      '@typescript-eslint/no-explicit-any': 'warn',
      
      // React specific rules for trading UI
      'react/prop-types': 'off', // Using TypeScript instead
      'react/react-in-jsx-scope': 'off', // Not needed in Next.js
      'react-hooks/exhaustive-deps': 'warn',
      
      // Next.js specific rules
      '@next/next/no-img-element': 'error',
      '@next/next/no-html-link-for-pages': 'error',
    },
  },
  
  // File-specific configurations
  {
    files: ['**/*.ts', '**/*.tsx'],
    languageOptions: {
      parser: '@typescript-eslint/parser',
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
        ecmaVersion: 'latest',
        sourceType: 'module',
      },
    },
  },
  
  // Test files configuration
  {
    files: ['**/*.test.ts', '**/*.test.tsx', '**/*.spec.ts', '**/*.spec.tsx'],
    rules: {
      'no-console': 'off',
      '@typescript-eslint/no-explicit-any': 'off',
    },
  },
  
  // Configuration files
  {
    files: ['*.config.js', '*.config.mjs', '*.config.ts'],
    rules: {
      'no-console': 'off',
    },
  },
  
  // Ignore patterns
  {
    ignores: [
      'node_modules/**',
      '.next/**',
      'out/**',
      'build/**',
      'dist/**',
      'coverage/**',
      '.nyc_output/**',
      'docs/api/**',
      'public/**',
      '*.min.js',
      'test-results/**',
    ],
  },
]; 