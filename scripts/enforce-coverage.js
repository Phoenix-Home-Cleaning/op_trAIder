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

import fs from 'fs';
import path from 'path';

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
      'apps/frontend/lib/trading/**',
      'apps/frontend/lib/risk/**',
      'apps/frontend/lib/signals/**',
      'apps/frontend/lib/execution/**',
      'apps/frontend/lib/market-data/**'
    ]
  },
  
  // Risk management thresholds (zero tolerance)
  risk: {
    lines: 100,
    branches: 100,
    functions: 100,
    statements: 100,
    paths: [
      'apps/backend/utils/risk',
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
  const coveragePath = path.join(process.cwd(), 'coverage', 'coverage-final.json');
  
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
    if (!fileData || !matchesPatterns(filePath, patterns)) {
      continue;
    }
    
    const s = fileData.s || {};
    const f = fileData.f || {};
    const b = fileData.b || {};
    const l = fileData.l || {};
    const fnMap = fileData.fnMap || {};
    
    totalLines += Object.keys(l).length;
    coveredLines += Object.values(l).filter(c => c > 0).length;
    
    totalBranches += Object.values(b).flat().length;
    coveredBranches += Object.values(b).flat().filter(c => c > 0).length;
    
    totalFunctions += Object.keys(fnMap).length;
    coveredFunctions += Object.values(f).filter(c => c > 0).length;
    
    totalStatements += Object.keys(s).length;
    coveredStatements += Object.values(s).filter(c => c > 0).length;
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
 * Get global coverage from the 'total' field in coverage-final.json
 * 
 * @param {Object} coverageData - Full coverage data from coverage-final.json
 * @returns {Object} Aggregated global coverage metrics
 */
function getGlobalCoverage(coverageData) {
  const total = Object.values(coverageData).reduce((acc, fileData) => {
    if (!fileData) {
      return acc;
    }
    
    const s = fileData.s || {};
    const f = fileData.f || {};
    const b = fileData.b || {};
    const l = fileData.l || {};
    const fnMap = fileData.fnMap || {};

    acc.totalLines += Object.keys(l).length;
    acc.coveredLines += Object.values(l).filter(c => c > 0).length;
    acc.totalBranches += Object.values(b).flat().length;
    acc.coveredBranches += Object.values(b).flat().filter(c => c > 0).length;
    acc.totalFunctions += Object.keys(fnMap).length;
    acc.coveredFunctions += Object.values(f).filter(c => c > 0).length;
    acc.totalStatements += Object.keys(s).length;
    acc.coveredStatements += Object.values(s).filter(c => c > 0).length;
    return acc;
  }, {
    totalLines: 0,
    coveredLines: 0,
    totalBranches: 0,
    coveredBranches: 0,
    totalFunctions: 0,
    coveredFunctions: 0,
    totalStatements: 0,
    coveredStatements: 0,
  });

  return {
    lines: total.totalLines > 0 ? (total.coveredLines / total.totalLines) * 100 : 100,
    branches: total.totalBranches > 0 ? (total.coveredBranches / total.totalBranches) * 100 : 100,
    functions: total.totalFunctions > 0 ? (total.coveredFunctions / total.totalFunctions) * 100 : 100,
    statements: total.totalStatements > 0 ? (total.coveredStatements / total.totalStatements) * 100 : 100,
    totals: {
      lines: { total: total.totalLines, covered: total.coveredLines },
      branches: { total: total.totalBranches, covered: total.coveredBranches },
      functions: { total: total.totalFunctions, covered: total.coveredFunctions },
      statements: { total: total.totalStatements, covered: total.coveredStatements },
    },
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
    if (metric === 'paths') {
      continue;
    }
    
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
    const coverageData = loadCoverageSummary();
    
    const globalCoverage = getGlobalCoverage(coverageData);
    const tradingCoverage = calculatePatternCoverage(coverageData, COVERAGE_CONFIG.trading.paths);
    const riskCoverage = calculatePatternCoverage(coverageData, COVERAGE_CONFIG.risk.paths);
    
    const globalResults = validateCoverage(globalCoverage, COVERAGE_CONFIG.global, 'Global');
    const tradingResults = validateCoverage(tradingCoverage, COVERAGE_CONFIG.trading, 'Trading Logic');
    const riskResults = validateCoverage(riskCoverage, COVERAGE_CONFIG.risk, 'Risk Management');
    
    const allResults = [globalResults, tradingResults, riskResults];
    const report = generateReport(allResults);
    
    // Save report for CI/CD
    const reportsDir = path.join(process.cwd(), 'coverage');
    fs.writeFileSync(path.join(reportsDir, 'enforcement-report.txt'), report);
    
    // Exit with appropriate code
    const allPassed = allResults.every(r => r.passed);
    process.exit(allPassed ? 0 : 1);
    
  } catch {
    process.exit(1);
  }
}

// Run the script
enforceCoverage();

export { enforceCoverage, COVERAGE_CONFIG }; 