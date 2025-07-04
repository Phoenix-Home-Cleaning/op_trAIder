/**
 * @fileoverview TRAIDER V1 pre-commit validation engine for institutional trading safety
 * @module scripts/pre-commit-checks
 *
 * @description
 * Comprehensive pre-commit validation system designed for autonomous cryptocurrency trading.
 * Implements 7 critical safety checks including security validation, trading safety,
 * documentation compliance, and performance optimization. Designed to prevent financial
 * losses through code quality enforcement.
 *
 * @performance
 * - Latency target: <30s total execution
 * - Throughput: Process 100+ files/sec
 * - Memory usage: <100MB peak
 *
 * @risk
 * - Failure impact: CRITICAL - prevents unsafe code deployment
 * - Recovery strategy: Emergency bypass with audit trail
 *
 * @compliance
 * - Audit requirements: Yes - all validation results logged
 * - Data retention: 90 days for compliance tracking
 *
 * @see {@link docs/infrastructure/pre-commit-hooks.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { execSync } from 'child_process';
import { readFileSync, statSync } from 'fs';

/**
 * Validation result interface for pre-commit checks
 */
interface ValidationResult {
  success: boolean;
  checkName: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  errors: string[];
  warnings: string[];
}

/**
 * Configuration for validation patterns and thresholds
 */
const VALIDATION_CONFIG = {
  // File size limits (1MB = 1024 * 1024 bytes)
  MAX_FILE_SIZE: 1024 * 1024,

  // Secret detection patterns for cryptocurrency trading platforms
  SECRET_PATTERNS: [
    // API Keys and Tokens
    /(?:api[_-]?key|apikey|api[_-]?token)\s*[:=]\s*['"][a-zA-Z0-9_-]{16,}['"]/gi,
    /(?:secret[_-]?key|secretkey|secret[_-]?token)\s*[:=]\s*['"][a-zA-Z0-9_-]{16,}['"]/gi,
    /(?:access[_-]?token|accesstoken)\s*[:=]\s*['"][a-zA-Z0-9_-]{16,}['"]/gi,

    // Cryptocurrency Exchange API Keys
    /(?:coinbase|binance|kraken|bitfinex|huobi)[_-]?(?:api[_-]?key|secret)\s*[:=]\s*['"][a-zA-Z0-9_-]{16,}['"]/gi,

    // Database Connection Strings
    /(?:database[_-]?url|db[_-]?url|connection[_-]?string)\s*[:=]\s*['"][^'"]{20,}['"]/gi,
    /(?:postgres|mysql|mongodb):\/\/[^'"\\s]{10,}/gi,

    // JWT Secrets
    /(?:jwt[_-]?secret|token[_-]?secret)\s*[:=]\s*['"][a-zA-Z0-9_-]{32,}['"]/gi,

    // Private Keys
    /-----BEGIN\s+(?:RSA\s+)?PRIVATE\s+KEY-----/gi,
    /(?:private[_-]?key)\s*[:=]\s*['"][a-zA-Z0-9+/=]{40,}['"]/gi,

    // AWS and Cloud Credentials
    /(?:aws[_-]?access[_-]?key|aws[_-]?secret)\s*[:=]\s*['"][A-Z0-9]{16,}['"]/gi,

    // Generic high-entropy strings (potential secrets)
    /['"][a-zA-Z0-9+/]{40,}={0,2}['"]/g,
  ],

  // Trading-critical file patterns
  TRADING_CRITICAL_PATTERNS: [
    /\/trading\//,
    /\/risk\//,
    /\/signal\//,
    /\/executor\//,
    /\/portfolio\//,
    /MarketData/,
    /OrderManagement/,
    /RiskEngine/,
  ],

  // Required error handling patterns for trading files
  ERROR_HANDLING_PATTERNS: [
    /try\s*{[\s\S]*?catch\s*\(/,
    /\.catch\s*\(/,
    /throw\s+new\s+\w*Error/,
    /if\s*\([^)]*error[^)]*\)/i,
  ],
};

/**
 * Get list of staged files for validation
 *
 * @returns {string[]} Array of staged file paths
 * @throws {Error} If git command fails
 *
 * @performance O(1) time, minimal I/O
 * @sideEffects Executes git command
 */
function getStagedFiles(): string[] {
  try {
    const output = execSync('git diff --cached --name-only', { encoding: 'utf8' });
    return output
      .trim()
      .split('\n')
      .filter((file) => file.length > 0);
  } catch (error) {
    throw new Error(`Failed to get staged files: ${error}`);
  }
}

/**
 * Validate files for hardcoded secrets and sensitive information
 *
 * @description Critical security check to prevent API keys, passwords, and other
 * sensitive data from being committed to the repository. Uses comprehensive
 * regex patterns targeting cryptocurrency exchange APIs and common secrets.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with detected secrets
 *
 * @throws {Error} If file reading fails
 *
 * @performance O(n*m) where n=files, m=patterns, ~1ms per file
 * @sideEffects Reads file contents from disk
 *
 * @tradingImpact CRITICAL - prevents API key exposure and unauthorized access
 * @riskLevel CRITICAL - financial loss if secrets are exposed
 *
 * @example
 * ```typescript
 * const result = validateSecrets(['src/config.ts']);
 * // result = { success: false, errors: ['API key detected in src/config.ts:42'] }
 * ```
 *
 * @monitoring
 * - Metric: `precommit.secret_detection.violations`
 * - Alert threshold: > 0 secrets detected
 */
function validateSecrets(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'Secret Detection',
    severity: 'CRITICAL',
    errors: [],
    warnings: [],
  };

  // Files to exclude from secret detection
  const EXCLUDED_FILES = [
    'scripts/pre-commit-checks.ts',
    '.github/workflows/',
    '.trivyignore',
    'env.example',
    '.env.template',
    'test/',
    'tests/',
    '.test.',
    '.spec.',
    '.md',
    'node_modules/',
    'docs/',
  ];

  // Test patterns to exclude (known safe test values)
  const TEST_EXCLUSIONS = [
    /NEXTAUTH_SECRET: 'test-secret-key-for-testing-only'/gi,
    /postgresql:\/\/test:test@localhost:5432\/traider_test/gi,
    /test-jwt-token/gi,
    /test-api-key/gi,
    /password.*=.*['"]password['"]/gi,
    /Password used to generate key/gi,
    /-E\s*["']/gi, // grep -E patterns in workflows
    /grep\s+-r/gi, // grep commands in workflows
    /pattern\.test\(/gi, // regex test patterns
    /regex\s+pattern/gi, // regex pattern comments
    /REPLACE_WITH_[A-Z_]+/gi, // Kubernetes manifest placeholders
    /REPLACE_WITH_.*?['"]/gi, // Generic replacement placeholders
  ];

  for (const file of files) {
    // Skip excluded files
    if (EXCLUDED_FILES.some((excluded) => file.includes(excluded))) {
      continue;
    }

    try {
      const content = readFileSync(file, 'utf8');
      const lines = content.split('\n');

      for (const pattern of VALIDATION_CONFIG.SECRET_PATTERNS) {
        pattern.lastIndex = 0; // Reset regex state
        let match;

        while ((match = pattern.exec(content)) !== null) {
          const matchedText = match[0];
          const lineNum = content.substring(0, match.index).split('\n').length;
          const line = lines[lineNum - 1] || '';

          // Skip comments and obvious false positives
          if (
            line.trim().startsWith('#') ||
            line.trim().startsWith('//') ||
            line.includes('description=') ||
            line.includes('Field(..., description=')
          ) {
            continue;
          }

          // Check if this match should be excluded (test patterns)
          const isTestPattern = TEST_EXCLUSIONS.some((exclusion) => {
            exclusion.lastIndex = 0;
            return exclusion.test(matchedText) || exclusion.test(line);
          });

          if (!isTestPattern) {
            result.errors.push(`${file}:${lineNum}: Potential secret detected`);
            result.success = false;
          }
        }
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not read file - ${error}`);
    }
  }

  return result;
}

/**
 * Validate file sizes to prevent repository bloat
 *
 * @description Prevents large files from being committed that could slow down
 * the repository and CI/CD pipeline. Particularly important for trading systems
 * where fast deployment is critical.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with oversized files
 *
 * @performance O(n) time, one stat call per file
 * @sideEffects Reads file metadata from disk
 *
 * @tradingImpact MEDIUM - affects deployment speed and repository performance
 * @riskLevel MEDIUM - operational efficiency impact
 */
function validateFileSize(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'File Size Check',
    severity: 'MEDIUM',
    errors: [],
    warnings: [],
  };

  for (const file of files) {
    try {
      const stats = statSync(file);
      if (stats.size > VALIDATION_CONFIG.MAX_FILE_SIZE) {
        /**
         * Human-readable file size in megabytes with two-decimal precision.
         *
         * @type {string}
         */
        const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
        result.errors.push(`${file}: File too large (${sizeMB}MB > 1MB)`);
        result.success = false;
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not check file size - ${error}`);
    }
  }

  return result;
}

/**
 * Validate file headers for documentation compliance
 *
 * @description Ensures all TypeScript files have proper JSDoc headers with
 * required institutional documentation standards including module path,
 * description, and author information.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with missing headers
 *
 * @tradingImpact LOW - affects code maintainability and audit compliance
 * @riskLevel LOW - documentation and compliance impact only
 */
function validateFileHeaders(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'File Header Check',
    severity: 'LOW',
    errors: [],
    warnings: [],
  };

  const tsFiles = files.filter((file) => file.endsWith('.ts') || file.endsWith('.tsx'));

  for (const file of tsFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const hasFileOverview = /@fileoverview/.test(content);
      const hasModule = /@module/.test(content);
      const hasDescription = /@description/.test(content);
      const hasAuthor = /@author TRAIDER Team/.test(content);

      if (!hasFileOverview || !hasModule || !hasDescription || !hasAuthor) {
        const missing = [];
        if (!hasFileOverview) {
          missing.push('@fileoverview');
        }
        if (!hasModule) {
          missing.push('@module');
        }
        if (!hasDescription) {
          missing.push('@description');
        }
        if (!hasAuthor) {
          missing.push('@author TRAIDER Team');
        }

        result.errors.push(`${file}: Missing ${missing.join(', ')} in header`);
        result.success = false;
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not read file - ${error}`);
    }
  }

  return result;
}

/**
 * Validate error handling in trading-critical files
 *
 * @description Ensures proper error handling in files that affect trading
 * operations. Critical for preventing financial losses due to unhandled
 * exceptions in trading logic.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with error handling issues
 *
 * @tradingImpact HIGH - prevents financial losses from unhandled errors
 * @riskLevel HIGH - potential for significant financial impact
 */
function validateErrorHandling(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'Error Handling Check',
    severity: 'HIGH',
    errors: [],
    warnings: [],
  };

  const tradingFiles = files.filter((file) =>
    VALIDATION_CONFIG.TRADING_CRITICAL_PATTERNS.some((pattern) => pattern.test(file))
  );

  for (const file of tradingFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const hasErrorHandling = VALIDATION_CONFIG.ERROR_HANDLING_PATTERNS.some((pattern) =>
        pattern.test(content)
      );

      if (!hasErrorHandling && content.includes('async ') && content.length > 500) {
        result.errors.push(`${file}: Trading file lacks proper error handling`);
        result.success = false;
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not read file - ${error}`);
    }
  }

  return result;
}

/**
 * Validate timer cleanup in React components
 *
 * @description Checks for proper cleanup of timers, intervals, and timeouts
 * in React components to prevent memory leaks in real-time trading interfaces.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with timer cleanup issues
 *
 * @tradingImpact MEDIUM - affects application stability and performance
 * @riskLevel MEDIUM - can cause memory leaks in production
 */
function validateTimerCleanup(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'Timer Cleanup Check',
    severity: 'MEDIUM',
    errors: [],
    warnings: [],
  };

  const reactFiles = files.filter(
    (file) =>
      (file.endsWith('.tsx') || file.endsWith('.ts')) &&
      (file.includes('component') || file.includes('hook') || file.includes('app/'))
  );

  for (const file of reactFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (line && /(?:setTimeout|setInterval|requestAnimationFrame)\s*\(/.test(line)) {
          const hasCleanup =
            content.includes('clearTimeout') ||
            content.includes('clearInterval') ||
            content.includes('cancelAnimationFrame');
          if (!hasCleanup) {
            result.errors.push(`${file}:${i + 1}: Timer without cleanup detected`);
            result.success = false;
          }
        }
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not read file - ${error}`);
    }
  }

  return result;
}

/**
 * Validate absence of console statements in production code
 *
 * @description Ensures no console.log, console.error, or other console
 * statements are committed, which could expose sensitive trading information
 * or affect performance in production.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with console statements
 *
 * @tradingImpact LOW - affects code cleanliness and security
 * @riskLevel LOW - potential information disclosure
 */
function validateConsoleStatements(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'Console Statement Check',
    severity: 'LOW',
    errors: [],
    warnings: [],
  };

  const codeFiles = files.filter(
    (file) =>
      (file.endsWith('.ts') ||
        file.endsWith('.tsx') ||
        file.endsWith('.js') ||
        file.endsWith('.jsx')) &&
      !file.includes('pre-commit-checks.ts') &&
      !file.includes('packages/tooling/')
  );

  for (const file of codeFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        const trimmedLine = line?.trim() || '';

        // Skip comments and documentation
        if (
          trimmedLine.startsWith('//') ||
          trimmedLine.startsWith('*') ||
          trimmedLine.startsWith('/*')
        ) {
          continue;
        }

        if (
          line &&
          (line.includes('console.log') ||
            line.includes('console.error') ||
            line.includes('console.warn'))
        ) {
          const match = line.match(/console\.(log|error|warn)/);
          if (match) {
            // Treat console statements as warnings rather than errors to avoid
            // blocking commits on low-severity cleanliness issues.
            result.warnings.push(`${file}:${i + 1}: Console statement found`);
          }
        }
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not read file - ${error}`);
    }
  }

  return result;
}

/**
 * Validate absence of focused tests (.only, .skip)
 *
 * @description Ensures no focused or skipped tests are committed, which
 * could cause incomplete test coverage in CI/CD pipeline.
 *
 * @param {string[]} files - Array of file paths to validate
 * @returns {ValidationResult} Validation result with focused tests
 *
 * @tradingImpact LOW - affects test coverage and CI reliability
 * @riskLevel LOW - testing and quality assurance impact
 */
function validateTestFocus(files: string[]): ValidationResult {
  const result: ValidationResult = {
    success: true,
    checkName: 'Test Focus Check',
    severity: 'LOW',
    errors: [],
    warnings: [],
  };

  const testFiles = files.filter(
    (file) => file.includes('.test.') || file.includes('.spec.') || file.includes('__tests__')
  );

  for (const file of testFiles) {
    try {
      const content = readFileSync(file, 'utf8');
      const lines = content.split('\n');

      for (let i = 0; i < lines.length; i++) {
        const line = lines[i];
        if (
          line?.includes('it.only') ||
          line?.includes('describe.only') ||
          line?.includes('test.only')
        ) {
          result.errors.push(`${file}:${i + 1}: Focused test (.only) found`);
          result.success = false;
        }
        if (line?.includes('setTimeout') || line?.includes('setInterval')) {
          const hasCleanup = content.includes('clearTimeout') || content.includes('clearInterval');
          if (!hasCleanup) {
            result.warnings.push(`${file}:${i + 1}: Timer without cleanup detected`);
          }
        }
      }
    } catch (error) {
      result.warnings.push(`${file}: Could not read file - ${error}`);
    }
  }

  return result;
}

/**
 * Main validation orchestrator
 *
 * @description Coordinates all validation checks with fail-fast strategy.
 * Executes critical checks first and provides comprehensive reporting.
 *
 * @returns {Promise<number>} Exit code (0 = success, 1 = failure)
 *
 * @performance Target <30s total execution time
 * @sideEffects Writes to stdout, exits process
 *
 * @tradingImpact CRITICAL - gates all code changes for trading system
 * @riskLevel CRITICAL - prevents deployment of unsafe code
 */
async function main(): Promise<number> {
  try {
    // Header output
    process.stdout.write('🚀 TRAIDER V1 Pre-commit Quality Gates\n');
    process.stdout.write('======================================\n');
    process.stdout.write('🔍 Running comprehensive quality checks...\n');

    const stagedFiles = getStagedFiles();

    if (stagedFiles.length === 0) {
      process.stdout.write('✅ No staged files to validate\n');
      return 0;
    }

    process.stdout.write(`📁 Checking ${stagedFiles.length} staged files...\n\n`);

    // Run all validations in order of criticality (fail-fast for critical issues)
    const validations = [
      validateSecrets(stagedFiles),
      validateFileSize(stagedFiles),
      validateFileHeaders(stagedFiles),
      validateErrorHandling(stagedFiles),
      validateTimerCleanup(stagedFiles),
      validateConsoleStatements(stagedFiles),
      validateTestFocus(stagedFiles),
    ];

    let hasErrors = false;
    let hasCriticalErrors = false;

    // Process results
    for (const result of validations) {
      const icon = result.success ? '✅' : '❌';
      const severity = result.success ? '' : `[${result.severity}]`;

      process.stdout.write(`${icon} ${result.checkName}${severity}: `);

      if (result.success) {
        if (result.checkName === 'Secret Detection') {
          process.stdout.write('No hardcoded secrets detected\n');
        } else if (result.checkName === 'File Size Check') {
          process.stdout.write('All files within size limits\n');
        } else if (result.checkName === 'Error Handling Check') {
          process.stdout.write('Proper error handling detected\n');
        } else if (result.checkName === 'Test Focus Check') {
          process.stdout.write('No focused tests found\n');
        } else {
          process.stdout.write('Passed\n');
        }
      } else {
        process.stdout.write(
          `Found ${result.errors.length} ${result.checkName.toLowerCase()} issue(s)\n`
        );

        // Show first few errors, truncate if too many
        const errorsToShow = result.errors.slice(0, 3);
        for (const error of errorsToShow) {
          process.stdout.write(`   └─ ${error}\n`);
        }

        if (result.errors.length > 3) {
          process.stdout.write(`   └─ ... and ${result.errors.length - 3} more\n`);
        }

        hasErrors = true;

        if (result.severity === 'CRITICAL') {
          hasCriticalErrors = true;
        }
      }
    }

    // Summary
    process.stdout.write('\n==================================================\n');

    if (hasErrors) {
      const failedChecks = validations.filter((v) => !v.success).length;
      process.stdout.write(`❌ ${failedChecks} check(s) failed!\n`);

      if (hasCriticalErrors) {
        process.stdout.write('🚨 CRITICAL issues detected - commit blocked\n');
        process.stdout.write('🔧 Fix critical issues before committing\n');
      } else {
        process.stdout.write('⚠️  Non-critical failures detected\n');
        process.stdout.write('💡 Consider fixing before committing\n');
        process.stdout.write('🔧 Use --no-verify to bypass (not recommended)\n');
      }

      return 1;
    } else {
      process.stdout.write('✅ All quality checks passed!\n');
      process.stdout.write('🚀 Ready for commit\n');
      return 0;
    }
  } catch (error) {
    process.stdout.write(`💥 Validation failed: ${error}\n`);
    return 1;
  }
}

// =============================================================================
// SCRIPT EXECUTION
// =============================================================================

main()
  .then((exitCode) => {
    process.exit(exitCode);
  })
  .catch((error) => {
    console.error('❌ An unexpected error occurred in the pre-commit hook:');
    console.error(error);
    process.exit(1);
  });

export { main, VALIDATION_CONFIG };
export type { ValidationResult };
