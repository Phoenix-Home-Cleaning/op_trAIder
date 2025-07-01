#!/usr/bin/env node

/**
 * @fileoverview Coverage Enforcement Script for TRAIDER V1
 * @module scripts/enforce-coverage
 * 
 * @description
 * Institutional-grade coverage enforcement with differentiated thresholds
 * for trading logic vs general application code. Ensures compliance with
 * institutional trading system standards.
 * 
 * @performance
 * - Execution time: <5s for full coverage analysis
 * - Memory usage: <100MB
 * 
 * @risk
 * - Failure impact: CRITICAL - Blocks deployments on coverage failures
 * - Recovery strategy: Fix tests or adjust legitimate threshold exceptions
 * 
 * @compliance
 * - Audit requirements: Yes - All coverage decisions logged
 * - Data retention: Coverage reports retained for 1 year
 * 
 * @see {@link docs/testing/coverage-enforcement.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

const fs = require('fs');
const path = require('path');

// =============================================================================
// CONFIGURATION - INSTITUTIONAL GRADE THRESHOLDS
// =============================================================================

const COVERAGE_CONFIG = {
  // Global thresholds (minimum acceptable)
  global: {
    lines: 80,
    branches: 80,
    functions: 80,
    statements: 80
  },
  
  // Trading logic thresholds (critical paths)
  trading: {
    lines: 90,
    branches: 90,
    functions: 90,
    statements: 90,
    paths: [
      'app/lib/trading/**',
      'app/lib/risk/**',
      'app/lib/signals/**',
      'app/lib/execution/**',
      'app/lib/market-data/**'
    ]
  },
  
  // Risk management thresholds (zero tolerance)
  risk: {
    lines: 100,
    branches: 100,
    functions: 100,
    statements: 100,
    paths: [
      'app/lib/risk/engine/**',
      'app/lib/risk/limits/**',
      'app/lib/risk/validation/**'
    ]
  }
};

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Load and parse coverage summary
 * 
 * @returns {Object} Parsed coverage data
 * @throws {Error} If coverage file not found or invalid
 */
function loadCoverageSummary() {
  const coveragePath = path.join(process.cwd(), 'coverage', 'coverage-summary.json');
  
  if (!fs.existsSync(coveragePath)) {
    throw new Error(`Coverage summary not found at ${coveragePath}`);
  }
  
  try {
    const coverageData = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
    return coverageData;
  } catch (error) {
    throw new Error(`Failed to parse coverage summary: ${error.message}`);
  }
}

/**
 * Check if a file path matches any of the given patterns
 * 
 * @param {string} filePath - File path to check
 * @param {string[]} patterns - Array of glob patterns
 * @returns {boolean} True if path matches any pattern
 */
function matchesPatterns(filePath, patterns) {
  return patterns.some(pattern => {
    const regex = new RegExp(pattern.replace(/\*\*/g, '.*').replace(/\*/g, '[^/]*'));
    return regex.test(filePath);
  });
}

/**
 * Calculate coverage for specific file patterns
 * 
 * @param {Object} coverageData - Full coverage data
 * @param {string[]} patterns - File patterns to include
 * @returns {Object} Aggregated coverage metrics
 */
function calculatePatternCoverage(coverageData, patterns) {
  let totalLines = 0;
  let coveredLines = 0;
  let totalBranches = 0;
  let coveredBranches = 0;
  let totalFunctions = 0;
  let coveredFunctions = 0;
  let totalStatements = 0;
  let coveredStatements = 0;
  
  for (const [filePath, fileData] of Object.entries(coverageData)) {
    if (filePath === 'total' || !matchesPatterns(filePath, patterns)) {
      continue;
    }
    
    totalLines += fileData.lines.total;
    coveredLines += fileData.lines.covered;
    totalBranches += fileData.branches.total;
    coveredBranches += fileData.branches.covered;
    totalFunctions += fileData.functions.total;
    coveredFunctions += fileData.functions.covered;
    totalStatements += fileData.statements.total;
    coveredStatements += fileData.statements.covered;
  }
  
  return {
    lines: totalLines > 0 ? (coveredLines / totalLines) * 100 : 100,
    branches: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 100,
    functions: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 100,
    statements: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 100,
    totals: {
      lines: { total: totalLines, covered: coveredLines },
      branches: { total: totalBranches, covered: coveredBranches },
      functions: { total: totalFunctions, covered: coveredFunctions },
      statements: { total: totalStatements, covered: coveredStatements }
    }
  };
}

/**
 * Validate coverage against thresholds
 * 
 * @param {Object} coverage - Coverage metrics
 * @param {Object} thresholds - Required thresholds
 * @param {string} category - Category name for reporting
 * @returns {Object} Validation results
 */
function validateCoverage(coverage, thresholds, category) {
  const results = {
    passed: true,
    category,
    failures: [],
    metrics: coverage
  };
  
  for (const [metric, threshold] of Object.entries(thresholds)) {
    if (metric === 'paths') continue;
    
    const actual = coverage[metric];
    if (actual < threshold) {
      results.passed = false;
      results.failures.push({
        metric,
        actual: actual.toFixed(2),
        required: threshold,
        gap: (threshold - actual).toFixed(2)
      });
    }
  }
  
  return results;
}

/**
 * Generate detailed coverage report
 * 
 * @param {Object[]} results - Array of validation results
 * @returns {string} Formatted report
 */
function generateReport(results) {
  let report = '\n🎯 TRAIDER V1 - Coverage Enforcement Report\n';
  report += '='.repeat(50) + '\n\n';
  
  let overallPassed = true;
  
  for (const result of results) {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    report += `${status} ${result.category.toUpperCase()} COVERAGE\n`;
    report += '-'.repeat(30) + '\n';
    
    // Show metrics
    report += `Lines:      ${result.metrics.lines.toFixed(2)}%\n`;
    report += `Branches:   ${result.metrics.branches.toFixed(2)}%\n`;
    report += `Functions:  ${result.metrics.functions.toFixed(2)}%\n`;
    report += `Statements: ${result.metrics.statements.toFixed(2)}%\n`;
    
    if (!result.passed) {
      overallPassed = false;
      report += '\n❌ FAILURES:\n';
      for (const failure of result.failures) {
        report += `  • ${failure.metric}: ${failure.actual}% (required: ${failure.required}%, gap: ${failure.gap}%)\n`;
      }
    }
    
    report += '\n';
  }
  
  // Overall result
  report += '='.repeat(50) + '\n';
  if (overallPassed) {
    report += '✅ ALL COVERAGE THRESHOLDS MET - DEPLOYMENT APPROVED\n';
  } else {
    report += '❌ COVERAGE THRESHOLDS NOT MET - DEPLOYMENT BLOCKED\n';
    report += '\n🔧 REMEDIATION REQUIRED:\n';
    report += '  1. Add tests for uncovered code paths\n';
    report += '  2. Focus on trading logic and risk management\n';
    report += '  3. Ensure critical paths have 100% coverage\n';
    report += '  4. Review and update test cases\n';
  }
  
  return report;
}

// =============================================================================
// MAIN EXECUTION
// =============================================================================

/**
 * Main coverage enforcement function
 */
async function enforceCoverage() {
  try {
    console.log('🔍 Starting coverage enforcement...\n');
    
    // Load coverage data
    const coverageData = loadCoverageSummary();
    const results = [];
    
    // Check global coverage
    const globalCoverage = coverageData.total;
    const globalResult = validateCoverage(
      {
        lines: globalCoverage.lines.pct,
        branches: globalCoverage.branches.pct,
        functions: globalCoverage.functions.pct,
        statements: globalCoverage.statements.pct
      },
      COVERAGE_CONFIG.global,
      'Global'
    );
    results.push(globalResult);
    
    // Check trading logic coverage
    const tradingCoverage = calculatePatternCoverage(coverageData, COVERAGE_CONFIG.trading.paths);
    const tradingResult = validateCoverage(
      tradingCoverage,
      COVERAGE_CONFIG.trading,
      'Trading Logic'
    );
    results.push(tradingResult);
    
    // Check risk management coverage
    const riskCoverage = calculatePatternCoverage(coverageData, COVERAGE_CONFIG.risk.paths);
    if (riskCoverage.totals.lines.total > 0) {
      const riskResult = validateCoverage(
        riskCoverage,
        COVERAGE_CONFIG.risk,
        'Risk Management'
      );
      results.push(riskResult);
    }
    
    // Generate and display report
    const report = generateReport(results);
    console.log(report);
    
    // Save report for CI/CD
    const reportsDir = path.join(process.cwd(), 'coverage');
    fs.writeFileSync(path.join(reportsDir, 'enforcement-report.txt'), report);
    
    // Exit with appropriate code
    const allPassed = results.every(r => r.passed);
    process.exit(allPassed ? 0 : 1);
    
  } catch (error) {
    console.error('❌ Coverage enforcement failed:', error.message);
    process.exit(1);
  }
}

// Run if called directly
if (require.main === module) {
  enforceCoverage();
}

module.exports = { enforceCoverage, COVERAGE_CONFIG }; 