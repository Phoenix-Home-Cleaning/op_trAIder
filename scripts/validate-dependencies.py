#!/usr/bin/env python3
"""
@fileoverview Dependency validation script for TRAIDER V1 backend
@module scripts/validate-dependencies

@description
World-class dependency validation script that ensures all critical dependencies
are properly installed and importable. This prevents runtime failures during
CI/CD pipeline execution and provides early detection of missing packages.

@performance
- Validation time: <5s for full dependency check
- Memory usage: <50MB
- Exit codes: 0 (success), 1 (missing deps), 2 (import errors)

@risk
- Failure impact: CRITICAL - Prevents deployment with missing dependencies
- Recovery strategy: Install missing packages and re-run validation

@compliance
- Audit requirements: Yes - tracks dependency versions
- Data retention: Validation logs retained for 30 days

@see {@link docs/infrastructure/dependency-management.md}
@since 1.0.0
@author TRAIDER Team
"""

import sys
import importlib
import subprocess
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dependency-validator')

# Log the Python path for diagnostics
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"sys.path: {json.dumps(sys.path, indent=2)}")

class DependencyValidator:
    """
    World-class dependency validation for institutional-grade trading platform.
    
    @description
    Validates that all critical dependencies are installed and importable,
    preventing runtime failures during trading operations.
    
    @performance O(n) time where n is number of dependencies
    @sideEffects None - read-only validation
    
    @tradingImpact Prevents trading system failures due to missing dependencies
    @riskLevel HIGH - Critical for system stability
    """
    
    # Critical dependencies that must be available for trading operations
    CRITICAL_DEPENDENCIES = {
        'fastapi': 'FastAPI web framework',
        'uvicorn': 'ASGI server',
        'pydantic': 'Data validation',
        'sqlalchemy': 'Database ORM',
        'alembic': 'Database migrations',
        'asyncpg': 'PostgreSQL async driver',
        'psycopg2': 'PostgreSQL sync driver',
        'pytest': 'Testing framework',
        'pytest-asyncio': 'Async testing support',
        'pytest-cov': 'Coverage reporting',
        'hypothesis': 'Property-based testing',
        'structlog': 'Structured logging',
        'loguru': 'Advanced logging',
        'jose': 'JWT handling',
        'passlib': 'Password hashing',
        'cryptography': 'Cryptographic operations',
        'httpx': 'HTTP client',
        'requests': 'HTTP requests',
        'pandas': 'Data processing',
        'numpy': 'Numerical computing',
        'scikit-learn': 'Machine learning',
        'ccxt': 'Exchange connectivity',
        'redis': 'Caching',
        'prometheus_client': 'Metrics collection',
    }
    
    # Import mappings for packages with different import names
    IMPORT_MAPPINGS = {
        'python-jose': 'jose',
        'python-multipart': 'multipart',
        'pytest-asyncio': 'pytest_asyncio',
        'pytest-cov': 'pytest_cov',
        'pytest-mock': 'pytest_mock',
        'pytest-ruff': 'pytest_ruff',
        'factory-boy': 'factory',
        'python-dotenv': 'dotenv',
        'python-decouple': 'decouple',
        'python-dateutil': 'dateutil',
        'prometheus-client': 'prometheus_client',
        'psycopg2-binary': 'psycopg2',
        'scikit-learn': 'sklearn',
        'pydantic-settings': 'pydantic_settings',
        'PyJWT': 'jwt',
        'pyyaml': 'yaml',
        'email-validator': 'email_validator',
        'pytest-xdist': 'xdist',
        'sentry-sdk': 'sentry_sdk',
        'sarif-om': 'sarif_om',
        'jschema-to-python': 'jschema_to_python',
        'coverage-badge': 'coverage_badge',
        'more-itertools': 'more_itertools',
    }
    
    def __init__(self, requirements_file: str = 'backend/requirements.txt'):
        """
        Initialize dependency validator.
        
        @param requirements_file Path to requirements.txt file
        @throws FileNotFoundError If requirements file doesn't exist
        """
        self.requirements_file = Path(requirements_file)
        if not self.requirements_file.exists():
            raise FileNotFoundError(f"Requirements file not found: {requirements_file}")
        
        self.validation_results: Dict[str, Dict] = {}
        self.missing_dependencies: List[str] = []
        self.import_errors: List[Tuple[str, str]] = []
    
    def parse_requirements(self) -> List[Tuple[str, str]]:
        """
        Parse requirements.txt file to extract package names and versions.
        
        @returns List of (package_name, version) tuples
        @throws ValueError If requirements file is malformed
        
        @performance O(n) where n is number of lines in requirements file
        @sideEffects None - read-only operation
        """
        dependencies = []
        
        try:
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse package==version format
                    if '==' in line:
                        package, version = line.split('==', 1)
                        # Handle extras like package[extra]==version
                        if '[' in package:
                            package = package.split('[')[0]
                        dependencies.append((package.strip(), version.strip()))
                    else:
                        logger.warning(f"Skipping malformed line {line_num}: {line}")
            
            logger.info(f"Parsed {len(dependencies)} dependencies from {self.requirements_file}")
            return dependencies
            
        except Exception as e:
            raise ValueError(f"Failed to parse requirements file: {e}")
    
    def check_package_installed(self, package: str, version: str) -> Dict:
        """
        Check if a package is installed with correct version.
        
        @param package Package name to check
        @param version Expected version
        @returns Dictionary with validation results
        
        @performance O(1) - single subprocess call
        @sideEffects None - read-only validation
        """
        try:
            # Check if package is installed
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'show', package],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                return {
                    'installed': False,
                    'version': None,
                    'expected_version': version,
                    'error': f"Package {package} not found"
                }
            
            # Parse version from pip show output
            installed_version = None
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    installed_version = line.split(':', 1)[1].strip()
                    break
            
            return {
                'installed': True,
                'version': installed_version,
                'expected_version': version,
                'version_match': installed_version == version,
                'error': None
            }
            
        except subprocess.TimeoutExpired:
            return {
                'installed': False,
                'version': None,
                'expected_version': version,
                'error': f"Timeout checking package {package}"
            }
        except Exception as e:
            return {
                'installed': False,
                'version': None,
                'expected_version': version,
                'error': f"Error checking package {package}: {e}"
            }
    
    def check_package_importable(self, package: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a package can be imported successfully.
        
        @param package Package name to import
        @returns Tuple of (importable, error_message)
        
        @performance O(1) - single import attempt
        @sideEffects None - import attempt only
        """
        # Use import mapping if available, otherwise replace hyphens
        import_name = self.IMPORT_MAPPINGS.get(package, package.replace('-', '_'))
        
        try:
            importlib.import_module(import_name)
            return True, None
        except ImportError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Unexpected error importing {import_name}: {e}"
    
    def validate_critical_dependencies(self) -> bool:
        """
        Validate that all critical dependencies are available.
        
        @returns True if all critical dependencies are valid
        
        @performance O(n) where n is number of critical dependencies
        @sideEffects Updates validation_results, missing_dependencies, import_errors
        """
        logger.info("Validating critical dependencies...")
        all_valid = True
        
        for package, description in self.CRITICAL_DEPENDENCIES.items():
            logger.debug(f"Checking critical dependency: {package}")
            
            # Check if package can be imported
            importable, error = self.check_package_importable(package)
            
            if not importable:
                logger.error(f"Critical dependency {package} ({description}) cannot be imported: {error}")
                self.missing_dependencies.append(package)
                self.import_errors.append((package, error))
                all_valid = False
            else:
                logger.debug(f"Critical dependency {package} is importable")
        
        return all_valid
    
    def validate_all_dependencies(self) -> bool:
        """
        Validate all dependencies from requirements.txt.
        
        @returns True if all dependencies are valid
        
        @performance O(n) where n is number of dependencies
        @sideEffects Updates validation_results with full dependency status
        """
        logger.info("Validating all dependencies...")
        dependencies = self.parse_requirements()
        all_valid = True
        
        for package, version in dependencies:
            logger.debug(f"Validating {package}=={version}")
            
            # Check installation status
            install_result = self.check_package_installed(package, version)
            
            # Check import status
            importable, import_error = self.check_package_importable(package)
            
            # Combine results
            self.validation_results[package] = {
                **install_result,
                'importable': importable,
                'import_error': import_error,
                'is_critical': package in self.CRITICAL_DEPENDENCIES
            }
            
            # Track failures
            if not install_result['installed']:
                self.missing_dependencies.append(package)
                all_valid = False
            
            if not importable:
                self.import_errors.append((package, import_error))
                all_valid = False
        
        return all_valid
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive validation report.
        
        @returns Dictionary with validation summary and details
        
        @performance O(n) where n is number of dependencies
        @sideEffects None - read-only report generation
        """
        total_deps = len(self.validation_results)
        missing_count = len(self.missing_dependencies)
        import_error_count = len(self.import_errors)
        
        success_rate = ((total_deps - missing_count - import_error_count) / total_deps * 100) if total_deps > 0 else 0
        
        return {
            'validation_summary': {
                'total_dependencies': total_deps,
                'missing_dependencies': missing_count,
                'import_errors': import_error_count,
                'success_rate': round(success_rate, 2),
                'all_valid': missing_count == 0 and import_error_count == 0
            },
            'missing_dependencies': self.missing_dependencies,
            'import_errors': dict(self.import_errors),
            'critical_dependencies_status': {
                package: self.validation_results.get(package, {}).get('importable', False)
                for package in self.CRITICAL_DEPENDENCIES
            },
            'detailed_results': self.validation_results
        }
    
    def print_summary(self):
        """
        Print validation summary to console.
        
        @performance O(n) where n is number of dependencies
        @sideEffects Prints to stdout
        """
        report = self.generate_report()
        summary = report['validation_summary']
        
        print(f"\n{'='*60}")
        print(f"TRAIDER V1 - Dependency Validation Report")
        print(f"{'='*60}")
        print(f"Total Dependencies: {summary['total_dependencies']}")
        print(f"Missing Dependencies: {summary['missing_dependencies']}")
        print(f"Import Errors: {summary['import_errors']}")
        print(f"Success Rate: {summary['success_rate']}%")
        print(f"Status: {'✅ PASS' if summary['all_valid'] else '❌ FAIL'}")
        
        if self.missing_dependencies:
            print(f"\n🚨 Missing Dependencies:")
            for dep in self.missing_dependencies:
                desc = self.CRITICAL_DEPENDENCIES.get(dep, 'Optional dependency')
                print(f"  - {dep}: {desc}")
        
        if self.import_errors:
            print(f"\n🚨 Import Errors:")
            for package, error in self.import_errors:
                print(f"  - {package}: {error}")
        
        print(f"\n{'='*60}")

def main():
    """
    Main entry point for dependency validation.
    
    @returns Exit code: 0 (success), 1 (missing deps), 2 (import errors)
    """
    try:
        validator = DependencyValidator()
        
        # First check critical dependencies
        critical_valid = validator.validate_critical_dependencies()
        
        # Then validate all dependencies
        all_valid = validator.validate_all_dependencies()
        
        # Generate and print report
        validator.print_summary()
        
        # Determine exit code
        if not critical_valid:
            logger.error("Critical dependencies validation failed")
            return 2
        elif not all_valid:
            logger.warning("Some non-critical dependencies validation failed")
            return 1
        else:
            logger.info("All dependencies validated successfully")
            return 0
            
    except Exception as e:
        logger.error(f"Dependency validation failed: {e}")
        return 2

if __name__ == '__main__':
    sys.exit(main()) 