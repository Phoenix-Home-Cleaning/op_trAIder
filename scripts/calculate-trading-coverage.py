#!/usr/bin/env python3
"""
@fileoverview Trading Logic Coverage Calculator
@module scripts/calculate-trading-coverage

@description
World-class coverage calculator for TRAIDER V1 trading logic components.
Analyzes Python coverage JSON reports to calculate precise trading logic coverage
for institutional-grade quality gates.

@performance
- Latency target: <100ms
- Memory usage: <10MB
- Handles coverage files up to 100MB

@risk
- Failure impact: CRITICAL (blocks deployment)
- Recovery strategy: Fallback to 0% coverage on parsing errors

@compliance
- Audit requirements: Yes
- Data retention: Coverage reports retained for 90 days

@see {@link docs/infrastructure/ci-cd-pipeline.md}
@since 1.0.0-alpha
@author TRAIDER Team
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import logging

# Configure logging for institutional-grade traceability
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    force=True
)
logger = logging.getLogger('trading-coverage')

class TradingCoverageCalculator:
    """
    Calculate trading logic coverage from Python coverage JSON reports.
    
    @description
    Institutional-grade coverage calculator that identifies trading-specific
    modules and calculates precise coverage metrics for quality gates.
    
    @performance O(n) time complexity where n = number of files in coverage report
    @riskLevel HIGH - Critical for deployment decisions
    
    @tradingImpact
    Determines if trading logic meets 90% coverage threshold for production deployment
    
    @example
    ```python
    calculator = TradingCoverageCalculator()
    coverage = calculator.calculate_from_file('coverage.json')
    print(f"Trading coverage: {coverage:.2f}%")
    ```
    """
    
    # Trading-specific file patterns (institutional-grade classification)
    TRADING_PATTERNS = [
        'models/position.py',
        'models\\position.py',
        'backend/models/position.py',
        'backend\\models\\position.py',
        'models/trade.py', 
        'models\\trade.py',
        'backend/models/trade.py',
        'backend\\models\\trade.py',
        'models/signal.py',
        'models\\signal.py',
        'backend/models/signal.py',
        'backend\\models\\signal.py',
        'models/market_data.py',
        'models\\market_data.py',
        'backend/models/market_data.py',
        'backend\\models\\market_data.py',
        'api/trading',
        'api\\trading',
        'backend/api/trading',
        'backend\\api\\trading',
        'services/trading',
        'services\\trading',
        'backend/services/trading',
        'backend\\services\\trading',
        'services/risk',
        'services\\risk',
        'backend/services/risk',
        'backend\\services\\risk',
        'services/execution',
        'services\\execution',
        'backend/services/execution',
        'backend\\services\\execution',
        'services/portfolio',
        'services\\portfolio',
        'backend/services/portfolio',
        'backend\\services\\portfolio',
        'utils/trading',
        'utils\\trading',
        'backend/utils/trading',
        'backend\\utils\\trading',
        'utils/risk',
        'utils\\risk',
        'backend/utils/risk',
        'backend\\utils\\risk',
        'engines/',
        'engines\\',
        'backend/engines/',
        'backend\\engines\\',
        'strategies/',
        'strategies\\',
        'backend/strategies/',
        'backend\\strategies\\',
        'indicators/',
        'indicators\\',
        'backend/indicators/',
        'backend\\indicators\\',
        'risk_management/',
        'risk_management\\',
        'backend/risk_management/',
        'backend\\risk_management\\',
        'execution/',
        'execution\\',
        'backend/execution/',
        'backend\\execution\\'
    ]
    
    # Critical trading modules (must have ≥95% coverage)
    CRITICAL_MODULES = [
        'models/position.py',
        'models\\position.py',
        'backend/models/position.py',
        'backend\\models\\position.py',
        'models/trade.py',
        'models\\trade.py',
        'backend/models/trade.py',
        'backend\\models\\trade.py',
        'services/risk',
        'services\\risk',
        'backend/services/risk',
        'backend\\services\\risk',
        'services/execution',
        'services\\execution',
        'backend/services/execution',
        'backend\\services\\execution'
    ]
    
    def __init__(self, coverage_file: Optional[str] = None):
        """
        Initialize trading coverage calculator.
        
        @param coverage_file Path to coverage JSON file
        @throws FileNotFoundError If coverage file doesn't exist
        """
        self.coverage_file = coverage_file or self._find_coverage_file()
        self.trading_files: Dict[str, Dict] = {}
        self.coverage_data: Dict = {}
        
        # Pre-compute normalized patterns for efficient matching
        self._normalised_patterns = [self._normalise(p) for p in self.TRADING_PATTERNS]
        self._normalised_critical = [self._normalise(p) for p in self.CRITICAL_MODULES]
        
    @staticmethod
    def _normalise(path: str) -> str:
        """
        Normalize path for robust cross-platform matching.
        
        @param path File path to normalize
        @returns Normalized path (lowercase, forward slashes)
        
        @performance O(n) where n = path length
        @tradingImpact CRITICAL - Enables accurate file pattern matching
        """
        return path.replace('\\', '/').lower()
        
    def _find_coverage_file(self) -> str:
        """
        Find the most recent coverage JSON file.
        
        @returns Path to coverage file
        @throws FileNotFoundError If no coverage file found
        
        @performance O(1) - checks predefined locations
        """
        possible_paths = [
            'coverage-fresh.json',
            'coverage/coverage.json', 
            'backend/coverage.json',
            'coverage.json'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found coverage file: {path}")
                return path
                
        raise FileNotFoundError("No coverage JSON file found")
    
    def _is_trading_file(self, filepath: str) -> bool:
        """
        Determine if a file contains trading logic.
        
        @param filepath File path to check
        @returns True if file contains trading logic
        
        @performance O(k) where k = number of trading patterns
        @tradingImpact Critical for accurate coverage calculation
        """
        # Normalize filepath for robust cross-platform matching
        normalised = self._normalise(filepath)
        
        for pattern in self._normalised_patterns:
            if pattern in normalised:
                logger.debug(f"Trading match: {filepath} ← {pattern}")
                return True
                
        return False
    
    def _is_critical_module(self, filepath: str) -> bool:
        """
        Determine if a file is a critical trading module.
        
        @param filepath File path to check
        @returns True if file is critical trading module
        
        @riskLevel CRITICAL - These modules must have ≥95% coverage
        """
        normalised = self._normalise(filepath)
        return any(pattern in normalised for pattern in self._normalised_critical)
    
    def load_coverage_data(self) -> None:
        """
        Load and parse coverage JSON data.
        
        @throws json.JSONDecodeError If coverage file is malformed
        @throws FileNotFoundError If coverage file doesn't exist
        
        @performance O(n) where n = size of coverage file
        @sideEffects Loads coverage data into memory
        """
        try:
            with open(self.coverage_file, 'r', encoding='utf-8') as f:
                self.coverage_data = json.load(f)
                
            logger.info(f"Loaded coverage data from {self.coverage_file}")
            
            # Validate coverage data structure
            if 'files' not in self.coverage_data:
                raise ValueError("Invalid coverage format: missing 'files' key")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse coverage JSON: {e}")
            raise
        except FileNotFoundError:
            logger.error(f"Coverage file not found: {self.coverage_file}")
            raise
    
    def identify_trading_files(self) -> None:
        """
        Identify all trading-related files in coverage data.
        
        @sideEffects Populates self.trading_files dictionary
        @performance O(n) where n = number of files in coverage
        """
        files_data = self.coverage_data.get('files', {})
        
        logger.debug(f"Checking {len(files_data)} files for trading patterns")
        
        for filepath, file_coverage in files_data.items():
            is_trading = self._is_trading_file(filepath)
            logger.debug(f"File: {filepath} -> Trading: {is_trading}")
            if is_trading:
                self.trading_files[filepath] = file_coverage
                
        logger.info(f"Identified {len(self.trading_files)} trading files")
        
        # Log critical modules for audit trail
        critical_files = [f for f in self.trading_files.keys() if self._is_critical_module(f)]
        if critical_files:
            logger.info(f"Critical trading modules: {critical_files}")
        
        # Debug: Log first few trading files found
        if self.trading_files:
            logger.debug(f"Trading files found: {list(self.trading_files.keys())[:5]}")
        else:
            logger.warning("No trading files found - this may indicate a pattern matching issue")
    
    def calculate_coverage(self) -> Tuple[float, Dict[str, float], List[str]]:
        """
        Calculate trading logic coverage metrics.
        
        @returns Tuple of (overall_coverage, file_coverages, critical_issues)
        
        @performance O(n) where n = number of trading files
        @tradingImpact Determines deployment readiness
        
        @example
        ```python
        coverage, files, issues = calculator.calculate_coverage()
        if coverage >= 90.0:
            print("✅ Trading coverage meets threshold")
        ```
        """
        if not self.trading_files:
            logger.warning("No trading files found")
            return 0.0, {}, ["No trading files identified"]
        
        total_statements = 0
        total_covered = 0
        file_coverages = {}
        critical_issues = []
        
        for filepath, file_data in self.trading_files.items():
            summary = file_data.get('summary', {})
            
            statements = summary.get('num_statements', 0)
            covered = summary.get('covered_lines', 0)
            coverage_pct = summary.get('percent_covered', 0.0)
            
            total_statements += statements
            total_covered += covered
            file_coverages[filepath] = coverage_pct
            
            # Check critical module thresholds
            if self._is_critical_module(filepath) and coverage_pct < 95.0:
                critical_issues.append(
                    f"Critical module {filepath} has {coverage_pct:.1f}% coverage (requires ≥95%)"
                )
        
        # Calculate overall trading coverage
        if total_statements == 0:
            overall_coverage = 0.0
            critical_issues.append("No executable statements found in trading files")
        else:
            overall_coverage = (total_covered / total_statements) * 100.0
        
        logger.info(f"Trading logic coverage: {overall_coverage:.2f}%")
        logger.info(f"Total statements: {total_statements}, Covered: {total_covered}")
        
        return overall_coverage, file_coverages, critical_issues
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive trading coverage report.
        
        @returns Detailed coverage report dictionary
        
        @compliance Generates audit-ready coverage report
        @performance O(n) where n = number of trading files
        """
        # Ensure data is loaded before generating report
        if not hasattr(self, 'coverage_data') or not self.coverage_data:
            self.load_coverage_data()
        if not self.trading_files:
            self.identify_trading_files()
            
        coverage_pct, file_coverages, issues = self.calculate_coverage()
        
        # Sort files by coverage (lowest first for attention)
        sorted_files = sorted(file_coverages.items(), key=lambda x: x[1])
        
        report = {
            'overall_coverage': round(coverage_pct, 2),
            'threshold_met': coverage_pct >= 90.0,
            'total_trading_files': len(self.trading_files),
            'critical_issues': issues,
            'file_details': [
                {
                    'file': filepath,
                    'coverage': round(coverage, 2),
                    'status': '✅' if coverage >= 90.0 else '❌',
                    'critical': self._is_critical_module(filepath)
                }
                for filepath, coverage in sorted_files
            ],
            'summary': {
                'files_above_90': len([c for c in file_coverages.values() if c >= 90.0]),
                'files_below_90': len([c for c in file_coverages.values() if c < 90.0]),
                'critical_modules_count': len([f for f in file_coverages.keys() if self._is_critical_module(f)])
            }
        }
        
        return report
    
    def calculate_from_file(self, coverage_file: Optional[str] = None) -> float:
        """
        Calculate trading coverage from specified file.
        
        @param coverage_file Path to coverage JSON file
        @returns Trading logic coverage percentage
        
        @performance O(n) where n = size of coverage file
        @throws Exception On file read or parsing errors
        """
        if coverage_file:
            self.coverage_file = coverage_file
            
        self.load_coverage_data()
        self.identify_trading_files()
        coverage_pct, _, _ = self.calculate_coverage()
        
        return coverage_pct


def main():
    """
    Main entry point for trading coverage calculation.
    
    @performance Target: <100ms execution time
    @riskLevel CRITICAL - Used in CI/CD deployment gates
    """
    parser = argparse.ArgumentParser(
        description='Calculate TRAIDER V1 trading logic coverage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python calculate-trading-coverage.py
  python calculate-trading-coverage.py --file coverage.json
  python calculate-trading-coverage.py --report --verbose
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        help='Path to coverage JSON file',
        type=str
    )
    
    parser.add_argument(
        '--report', '-r',
        help='Generate detailed report',
        action='store_true'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        help='Enable verbose logging',
        action='store_true'
    )
    
    parser.add_argument(
        '--threshold', '-t',
        help='Coverage threshold (default: 90.0)',
        type=float,
        default=90.0
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        calculator = TradingCoverageCalculator(args.file)
        
        if args.report:
            # Generate detailed report
            report = calculator.generate_report()
            
            print("TRAIDER V1 Trading Logic Coverage Report")
            print("=" * 50)
            print(f"Overall Coverage: {report['overall_coverage']:.2f}%")
            print(f"Threshold: {args.threshold}%")
            print(f"Status: {'PASSED' if report['threshold_met'] else 'FAILED'}")
            print(f"Trading Files: {report['total_trading_files']}")
            print()
            
            if report['critical_issues']:
                print("Critical Issues:")
                for issue in report['critical_issues']:
                    print(f"  - {issue}")
                print()
            
            print("File Coverage Details:")
            for file_detail in report['file_details']:
                critical_marker = " [CRITICAL]" if file_detail['critical'] else ""
                status_marker = "PASS" if file_detail['coverage'] >= 90.0 else "FAIL"
                print(f"  {status_marker} {file_detail['file']}: {file_detail['coverage']:.1f}%{critical_marker}")
            
            print()
            print(f"Summary: {report['summary']['files_above_90']} files ≥90%, {report['summary']['files_below_90']} files <90%")
            
            # Exit with appropriate code
            sys.exit(0 if report['threshold_met'] else 1)
        else:
            # Simple coverage calculation
            coverage = calculator.calculate_from_file()
            print(f"{coverage:.2f}")
            
            # Exit with appropriate code for CI
            sys.exit(0 if coverage >= args.threshold else 1)
            
    except Exception as e:
        logger.error(f"Failed to calculate trading coverage: {e}")
        print("0.0")  # Safe fallback for CI
        sys.exit(1)


if __name__ == '__main__':
    main() 