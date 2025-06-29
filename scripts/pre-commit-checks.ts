/**
 * @fileoverview Comprehensive pre-commit quality checks for TRAIDER V1
 * @module scripts/pre-commit-checks
 * 
 * @description
 * Institutional-grade pre-commit validation ensuring code quality, security,
 * and trading system integrity. Performs static analysis, security scanning,
 * and trading-specific validation before allowing commits.
 * 
 * @performance
 * - Target runtime: <30 seconds
 * - Parallel execution where possible
 * - Early exit on critical failures
 * 
 * @risk
 * - Failure impact: CRITICAL - prevents bad code from entering repository
 * - Recovery strategy: Clear error messages with fix suggestions
 * 
 * @compliance
 * - Audit requirements: Yes - all checks logged
 * - Security scanning: API keys, secrets, large files
 * 
 * @see {@link docs/infrastructure/pre-commit-hooks.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { execSync } from 'child_process';
import { readFileSync, statSync } from 'fs';

interface CheckResult {
  name: string;
  passed: boolean;
  message: string;
  details?: string[];
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
}

class PreCommitChecker {
  private results: CheckResult[] = [];
  private stagedFiles: string[] = [];

  constructor() {
    this.getStagedFiles();
  }

  /**
   * Get list of staged files for commit
   * 
   * @description Retrieves all staged files to focus checks on changed code
   * @returns Array of staged file paths
   */
  private getStagedFiles(): void {
    try {
      const output = execSync('git diff --cached --name-only', { encoding: 'utf8' });
      this.stagedFiles = output.trim().split('\n').filter(file => file.length > 0);
    } catch {
      this.stagedFiles = [];
    }
  }

  /**
   * Check for hardcoded secrets and API keys
   * 
   * @description Scans staged files for potential security vulnerabilities
   * @returns CheckResult indicating security status
   * 
   * @risk HIGH - Hardcoded secrets can lead to security breaches
   * @tradingImpact Could expose trading API keys or database credentials
   */
  private checkSecrets(): CheckResult {
    const secretPatterns = [
      /(?:api[_-]?key|secret[_-]?key|access[_-]?token|private[_-]?key)\s*[:=]\s*['"]\w{20,}['"]/i,
      /(?:password|passwd|pwd)\s*[:=]\s*['"]\w{8,}['"]/i,
      /(?:coinbase|binance|kraken)[_-]?(?:api[_-]?key|secret)\s*[:=]\s*['"]\w+['"]/i,
      /(?:postgres|postgresql|mysql|redis)[_-]?(?:password|pwd)\s*[:=]\s*['"]\w+['"]/i,
      /(?:jwt[_-]?secret|session[_-]?secret)\s*[:=]\s*['"]\w{32,}['"]/i,
    ];

    const violations: string[] = [];
    
    for (const file of this.stagedFiles) {
      if (file.match(/\.(ts|tsx|js|jsx|py|json|env)$/)) {
        try {
          const content = readFileSync(file, 'utf8');
          for (const pattern of secretPatterns) {
            const matches = content.match(pattern);
            if (matches) {
              violations.push(`${file}: Potential secret detected - ${matches[0].substring(0, 50)}...`);
            }
          }
        } catch {
          // File might be deleted, skip
        }
      }
    }

    return {
      name: 'Secret Detection',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'No hardcoded secrets detected' 
        : `Found ${violations.length} potential secret(s)`,
      details: violations,
      severity: 'CRITICAL'
    };
  }

  /**
   * Check for large files that shouldn't be committed
   * 
   * @description Prevents accidentally committing large binary files or datasets
   * @returns CheckResult indicating file size compliance
   * 
   * @risk MEDIUM - Large files slow down repository operations
   * @tradingImpact Large model files should be stored in MLflow, not git
   */
  private checkFileSize(): CheckResult {
    const maxSizeBytes = 1024 * 1024; // 1MB
    const violations: string[] = [];

    for (const file of this.stagedFiles) {
      try {
        const stats = statSync(file);
        if (stats.size > maxSizeBytes) {
          const sizeMB = (stats.size / (1024 * 1024)).toFixed(2);
          violations.push(`${file}: ${sizeMB}MB (exceeds 1MB limit)`);
        }
      } catch {
        // File might be deleted, skip
      }
    }

    return {
      name: 'File Size Check',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'All files within size limits' 
        : `Found ${violations.length} oversized file(s)`,
      details: violations,
      severity: 'MEDIUM'
    };
  }

  /**
   * Ensure new TypeScript files have proper header comments
   * 
   * @description Validates that new files include required documentation headers
   * @returns CheckResult indicating documentation compliance
   * 
   * @risk LOW - Missing documentation reduces code maintainability
   * @tradingImpact Proper documentation critical for trading system reliability
   */
  private checkFileHeaders(): CheckResult {
    const violations: string[] = [];
    const requiredPatterns = [
      /@fileoverview/,
      /@module/,
      /@description/,
      /@author TRAIDER Team/
    ];

    for (const file of this.stagedFiles) {
      if (file.match(/\.(ts|tsx)$/) && !file.includes('test') && !file.includes('spec')) {
        try {
          const content = readFileSync(file, 'utf8');
          const firstLines = content.split('\n').slice(0, 20).join('\n');
          
          for (const pattern of requiredPatterns) {
            if (!pattern.test(firstLines)) {
              violations.push(`${file}: Missing ${pattern.source} in header`);
            }
          }
        } catch {
          // File might be deleted, skip
        }
      }
    }

    return {
      name: 'File Header Check',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'All files have proper headers' 
        : `Found ${violations.length} file(s) missing headers`,
      details: violations,
      severity: 'LOW'
    };
  }

  /**
   * Check for proper error handling in trading-critical files
   * 
   * @description Ensures trading services implement proper error handling
   * @returns CheckResult indicating error handling compliance
   * 
   * @risk HIGH - Poor error handling can cause trading losses
   * @tradingImpact Unhandled errors in trading logic can lead to financial loss
   */
  private checkErrorHandling(): CheckResult {
    const violations: string[] = [];
    const tradingFiles = this.stagedFiles.filter(file => 
      file.includes('trading') || 
      file.includes('risk') || 
      file.includes('signal') || 
      file.includes('executor') ||
      file.includes('portfolio')
    );

    for (const file of tradingFiles) {
      if (file.match(/\.(ts|tsx)$/)) {
        try {
          const content = readFileSync(file, 'utf8');
          
          // Check for async functions without try-catch
          const asyncFunctions = content.match(/async\s+\w+\s*\([^)]*\)\s*{[^}]*}/g) || [];
          for (const func of asyncFunctions) {
            if (!func.includes('try') && !func.includes('catch')) {
              violations.push(`${file}: Async function without error handling`);
            }
          }

          // Check for API calls without error handling
          if (content.includes('fetch(') || content.includes('axios.')) {
            if (!content.includes('catch') && !content.includes('try')) {
              violations.push(`${file}: API calls without error handling`);
            }
          }
        } catch {
          // File might be deleted, skip
        }
      }
    }

    return {
      name: 'Error Handling Check',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'Proper error handling detected' 
        : `Found ${violations.length} error handling issue(s)`,
      details: violations,
      severity: 'HIGH'
    };
  }

  /**
   * Check for setTimeout without proper cleanup
   * 
   * @description Ensures timers are properly cleaned up to prevent memory leaks
   * @returns CheckResult indicating timer management compliance
   * 
   * @risk MEDIUM - Memory leaks can degrade system performance
   * @tradingImpact Performance degradation affects trading latency
   */
  private checkTimerCleanup(): CheckResult {
    const violations: string[] = [];

    for (const file of this.stagedFiles) {
      if (file.match(/\.(ts|tsx|js|jsx)$/)) {
        try {
          const content = readFileSync(file, 'utf8');
          const lines = content.split('\n');
          
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line && (line.includes('setTimeout') || line.includes('setInterval'))) {
              // Look for clearTimeout/clearInterval in the same function or useEffect cleanup
              const contextLines = lines.slice(Math.max(0, i - 10), i + 10).join('\n');
              if (!contextLines.includes('clearTimeout') && 
                  !contextLines.includes('clearInterval') &&
                  !contextLines.includes('return () =>')) {
                violations.push(`${file}:${i + 1}: Timer without cleanup detected`);
              }
            }
          }
        } catch {
          // File might be deleted, skip
        }
      }
    }

    return {
      name: 'Timer Cleanup Check',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'All timers have proper cleanup' 
        : `Found ${violations.length} timer cleanup issue(s)`,
      details: violations,
      severity: 'MEDIUM'
    };
  }

  /**
   * Check for console.log statements in production code
   * 
   * @description Ensures no debug statements are left in production code
   * @returns CheckResult indicating console statement compliance
   * 
   * @risk LOW - Console statements can expose sensitive information
   * @tradingImpact Debug statements may leak trading strategies or positions
   */
  private checkConsoleStatements(): CheckResult {
    const violations: string[] = [];

    for (const file of this.stagedFiles) {
      if (file.match(/\.(ts|tsx|js|jsx)$/) && !file.includes('test') && !file.includes('spec')) {
        try {
          const content = readFileSync(file, 'utf8');
          const lines = content.split('\n');
          
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line && line.match(/console\.(log|warn|error|info|debug)/)) {
              violations.push(`${file}:${i + 1}: ${line.trim()}`);
            }
          }
        } catch {
          // File might be deleted, skip
        }
      }
    }

    return {
      name: 'Console Statement Check',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'No console statements found' 
        : `Found ${violations.length} console statement(s)`,
      details: violations,
      severity: 'LOW'
    };
  }

  /**
   * Check for .only() in test files
   * 
   * @description Ensures test files don't have focused tests that skip others
   * @returns CheckResult indicating test focus compliance
   * 
   * @risk MEDIUM - Focused tests can hide failing tests
   * @tradingImpact Skipped tests may miss critical trading logic bugs
   */
  private checkTestFocus(): CheckResult {
    const violations: string[] = [];

    for (const file of this.stagedFiles) {
      if (file.match(/\.(test|spec)\.(ts|tsx|js|jsx)$/)) {
        try {
          const content = readFileSync(file, 'utf8');
          const lines = content.split('\n');
          
          for (let i = 0; i < lines.length; i++) {
            const line = lines[i];
            if (line && line.match(/\.(only|skip)\s*\(/)) {
              violations.push(`${file}:${i + 1}: ${line.trim()}`);
            }
          }
        } catch {
          // File might be deleted, skip
        }
      }
    }

    return {
      name: 'Test Focus Check',
      passed: violations.length === 0,
      message: violations.length === 0 
        ? 'No focused tests found' 
        : `Found ${violations.length} focused test(s)`,
      details: violations,
      severity: 'MEDIUM'
    };
  }

  /**
   * Run all pre-commit checks
   * 
   * @description Executes all validation checks and reports results
   * @returns Promise resolving to overall success status
   * 
   * @performance Runs checks in parallel where possible
   * @sideEffects Logs results to console, exits process on failure
   */
  public async runAllChecks(): Promise<boolean> {
    console.log('🚀 TRAIDER V1 Pre-commit Quality Gates');
    console.log('======================================');
    console.log(`📁 Checking ${this.stagedFiles.length} staged files...\n`);

    // Run all checks
    this.results = [
      this.checkSecrets(),
      this.checkFileSize(),
      this.checkFileHeaders(),
      this.checkErrorHandling(),
      this.checkTimerCleanup(),
      this.checkConsoleStatements(),
      this.checkTestFocus()
    ];

    // Report results
    let hasFailures = false;
    let hasCriticalFailures = false;

    for (const result of this.results) {
      const icon = result.passed ? '✅' : '❌';
      const severity = result.passed ? '' : ` [${result.severity}]`;
      
      console.log(`${icon} ${result.name}${severity}: ${result.message}`);
      
      if (!result.passed && result.details) {
        for (const detail of result.details.slice(0, 5)) { // Limit output
          console.log(`   └─ ${detail}`);
        }
        if (result.details.length > 5) {
          console.log(`   └─ ... and ${result.details.length - 5} more`);
        }
      }
      
      if (!result.passed) {
        hasFailures = true;
        if (result.severity === 'CRITICAL' || result.severity === 'HIGH') {
          hasCriticalFailures = true;
        }
      }
    }

    console.log('\n' + '='.repeat(50));
    
    if (!hasFailures) {
      console.log('✅ All pre-commit checks passed!');
      console.log('🎯 Ready for institutional-grade commit!');
      return true;
    } else {
      const failedCount = this.results.filter(r => !r.passed).length;
      console.log(`❌ ${failedCount} check(s) failed!`);
      
      if (hasCriticalFailures) {
        console.log('🚨 CRITICAL failures detected - commit blocked!');
        console.log('💡 Fix all issues before committing');
      } else {
        console.log('⚠️  Non-critical failures detected');
        console.log('💡 Consider fixing before committing');
        console.log('🔧 Use --no-verify to bypass (not recommended)');
      }
      
      return !hasCriticalFailures;
    }
  }
}

// Main execution
if (require.main === module) {
  const checker = new PreCommitChecker();
  checker.runAllChecks().then(success => {
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('💥 Pre-commit checks failed with error:', error);
    process.exit(1);
  });
}

export { PreCommitChecker }; 