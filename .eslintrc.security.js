/**
 * @fileoverview Security-focused ESLint Configuration for TRAIDER V1
 * @module .eslintrc.security
 * 
 * @description
 * Enhanced ESLint configuration focused on security vulnerabilities and
 * trading-specific security patterns for institutional-grade code analysis.
 * 
 * @performance
 * - Analysis target: <2min for full codebase
 * - Memory usage: <500MB
 * 
 * @risk
 * - Failure impact: HIGH - Security issues block deployments
 * - Recovery strategy: Fix security issues or document exceptions
 * 
 * @compliance
 * - Audit requirements: Yes - All security findings logged
 * - Standards: OWASP, CWE, SANS Top 25
 * 
 * @see {@link docs/security/eslint-security-config.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

export default {
  extends: [
    'eslint:recommended',
    '@typescript-eslint/recommended',
    'plugin:security/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking'
  ],
  
  parser: '@typescript-eslint/parser',
  
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
  },
  
  plugins: [
    '@typescript-eslint',
    'security'
  ],
  
  env: {
    node: true,
    es2022: true,
    browser: true
  },
  
  rules: {
    // =============================================================================
    // SECURITY RULES - CRITICAL FOR TRADING SYSTEMS
    // =============================================================================
    
    // Prevent dangerous eval usage
    'security/detect-eval-with-expression': 'error',
    'no-eval': 'error',
    'no-implied-eval': 'error',
    
    // Prevent unsafe regular expressions (ReDoS attacks)
    'security/detect-unsafe-regex': 'error',
    
    // Prevent buffer vulnerabilities
    'security/detect-buffer-noassert': 'error',
    'security/detect-new-buffer': 'error',
    
    // Prevent child process vulnerabilities
    'security/detect-child-process': 'warn',
    
    // Prevent non-literal require (code injection)
    'security/detect-non-literal-require': 'error',
    'security/detect-non-literal-fs-filename': 'error',
    
    // Prevent object injection
    'security/detect-object-injection': 'warn',
    
    // Prevent possible timing attacks
    'security/detect-possible-timing-attacks': 'error',
    
    // Prevent pseudoRandomBytes usage
    'security/detect-pseudoRandomBytes': 'error',
    
    // =============================================================================
    // TRADING-SPECIFIC SECURITY RULES
    // =============================================================================
    
    // Prevent hardcoded secrets (critical for trading APIs)
    'no-secrets/no-secrets': 'error',
    
    // Prevent debugger statements
    'no-debugger': 'error',
    
    // Prevent alert/confirm/prompt (not applicable in trading systems)
    'no-alert': 'error',
    
    // =============================================================================
    // TYPE SAFETY RULES (CRITICAL FOR TRADING CALCULATIONS)
    // =============================================================================
    
    // Prevent unsafe any usage
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unsafe-any': 'error',
    '@typescript-eslint/no-unsafe-assignment': 'error',
    '@typescript-eslint/no-unsafe-call': 'error',
    '@typescript-eslint/no-unsafe-member-access': 'error',
    '@typescript-eslint/no-unsafe-return': 'error',
    
    // Prevent null/undefined issues
    '@typescript-eslint/strict-boolean-expressions': 'error',
    
    // Prevent floating promises (critical in async trading operations)
    '@typescript-eslint/no-floating-promises': 'error',
    '@typescript-eslint/no-misused-promises': 'error',
    
    // =============================================================================
    // CODE QUALITY RULES FOR SECURITY
    // =============================================================================
    
    // Prevent unused variables (potential information disclosure)
    '@typescript-eslint/no-unused-vars': ['error', { 
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],
    
    // Prevent unreachable code
    'no-unreachable': 'error',
    
    // Prevent duplicate keys
    'no-dupe-keys': 'error',
    
    // Prevent redeclaring variables
    'no-redeclare': 'error',
    
    // =============================================================================
    // ASYNC/AWAIT SECURITY
    // =============================================================================
    
    // Prevent unhandled promise rejections
    'no-async-promise-executor': 'error',
    'no-await-in-loop': 'warn',
    'no-promise-executor-return': 'error',
    
    // =============================================================================
    // INPUT VALIDATION RULES
    // =============================================================================
    
    // Prevent prototype pollution
    'no-prototype-builtins': 'error',
    
    // Prevent unsafe property access
    'dot-notation': ['error', { allowKeywords: true }],
    
    // =============================================================================
    // TRADING-SPECIFIC OVERRIDES
    // =============================================================================
    
    // Allow console in trading alerts and monitoring
    'no-console': ['warn', { 
      allow: ['warn', 'error', 'info'] 
    }],
    
    // Strict non-null assertions for trading data
    '@typescript-eslint/no-non-null-assertion': 'error'
  },
  
  overrides: [
    {
      // Stricter rules for trading logic
      files: [
        'app/lib/trading/**/*.ts',
        'app/lib/risk/**/*.ts',
        'app/lib/signals/**/*.ts',
        'app/lib/execution/**/*.ts'
      ],
      rules: {
        // Zero tolerance for any type in trading logic
        '@typescript-eslint/no-explicit-any': 'error',
        '@typescript-eslint/no-unsafe-any': 'error',
        
        // Require explicit return types for trading functions
        '@typescript-eslint/explicit-function-return-type': 'error',
        
        // Prevent floating point precision issues
        'no-floating-decimal': 'error',
        
        // Require strict equality
        'eqeqeq': ['error', 'always'],
        
        // Prevent implicit type coercion
        'no-implicit-coercion': 'error'
      }
    },
    
    {
      // API route security
      files: ['app/api/**/*.ts'],
      rules: {
        // Strict input validation
        'security/detect-object-injection': 'error',
        
        // Prevent information disclosure
        'no-console': 'error',
        
        // Require explicit error handling
        '@typescript-eslint/no-floating-promises': 'error'
      }
    },
    
    {
      // Test files - relaxed rules
      files: [
        'tests/**/*.ts',
        'tests/**/*.tsx',
        '**/*.test.ts',
        '**/*.test.tsx',
        '**/*.spec.ts',
        '**/*.spec.tsx'
      ],
      rules: {
        // Allow any in tests for mocking
        '@typescript-eslint/no-explicit-any': 'warn',
        '@typescript-eslint/no-unsafe-any': 'warn',
        
        // Allow console in tests
        'no-console': 'off',
        
        // Allow non-null assertions in tests
        '@typescript-eslint/no-non-null-assertion': 'warn'
      }
    }
  ],
  
  settings: {
    // Security plugin settings
    security: {
      // Custom security rules for trading systems
      customRules: {
        'detect-hardcoded-credentials': true,
        'detect-sql-injection': true,
        'detect-xss': true
      }
    }
  },
  
  ignorePatterns: [
    'node_modules/',
    '.next/',
    'dist/',
    'build/',
    'coverage/',
    '*.config.js',
    '*.config.ts',
    'backend/',
    'infrastructure/',
    'docs/'
  ]
}; 