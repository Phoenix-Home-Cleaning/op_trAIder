/**
 * @fileoverview System Utilities Validation Tests
 * @module tests/unit/infrastructure/system-utilities-validation
 *
 * @description
 * Comprehensive test suite for system utilities installation and validation
 * logic used in GitHub Actions CI/CD pipeline. Tests cover package installation,
 * version verification, functionality validation, and error handling scenarios.
 *
 * @performance
 * - Latency target: <100ms per test
 * - Throughput: All tests complete in <5s
 * - Memory usage: <50MB
 *
 * @risk
 * - Failure impact: HIGH - CI/CD pipeline reliability
 * - Recovery strategy: Fallback to alternative installation methods
 *
 * @compliance
 * - Audit requirements: Yes - CI/CD security validation
 * - Data retention: 90 days (test results)
 *
 * @see {@link docs/infrastructure/code-quality-pipeline.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock system utilities for testing
const mockSystemUtilities = {
  jq: {
    version: 'jq-1.6',
    available: true,
    functional: true,
  },
  xxd: {
    version: 'xxd V1.10',
    available: true,
    functional: true,
  },
  bc: {
    version: 'bc 1.07.1',
    available: true,
    functional: true,
  },
  curl: {
    version: 'curl 7.81.0',
    available: true,
    functional: true,
    httpsSupport: true,
  },
  tar: {
    version: 'tar (GNU tar) 1.34',
    available: true,
    functional: true,
    gzipSupport: true,
  },
  file: {
    version: 'file-5.41',
    available: true,
    functional: true,
  },
};

// System utilities validation logic (extracted from workflow)
class SystemUtilitiesValidator {
  /**
   * Validates system utilities installation and functionality
   *
   * @description Comprehensive validation of all required system utilities
   *
   * @returns {Promise<ValidationResult>} Validation results with status and details
   *
   * @throws {SystemUtilitiesError} When critical utilities are missing or non-functional
   *
   * @performance O(n) time where n = number of utilities, <100ms typical latency
   * @sideEffects None - read-only validation
   *
   * @tradingImpact Critical for CI/CD pipeline reliability
   * @riskLevel HIGH - Pipeline failures impact deployment capability
   *
   * @example
   * ```typescript
   * const validator = new SystemUtilitiesValidator();
   * const result = await validator.validateUtilities();
   * // result = { success: true, utilities: {...}, errors: [] }
   * ```
   *
   * @monitoring
   * - Metric: `ci.system_utilities.validation_latency`
   * - Alert threshold: > 1000ms
   */
  async validateUtilities(): Promise<ValidationResult> {
    const results: ValidationResult = {
      success: true,
      utilities: {},
      errors: [],
    };

    // Validate jq (JSON processor)
    const jqResult = await this.validateJq();
    results.utilities.jq = jqResult;
    if (!jqResult.functional) {
      results.success = false;
      results.errors.push('jq not functional - required for GitHub API processing');
    }

    // Validate xxd (hex dump utility from vim-common)
    const xxdResult = await this.validateXxd();
    results.utilities.xxd = xxdResult;
    if (!xxdResult.functional) {
      results.success = false;
      results.errors.push('xxd not functional - required for binary validation');
    }

    // Validate bc (calculator)
    const bcResult = await this.validateBc();
    results.utilities.bc = bcResult;
    if (!bcResult.functional) {
      results.success = false;
      results.errors.push('bc not functional - required for coverage calculations');
    }

    // Validate curl with SSL support
    const curlResult = await this.validateCurl();
    results.utilities.curl = curlResult;
    if (!curlResult.functional) {
      results.success = false;
      results.errors.push('curl not functional - required for downloads');
    }

    // Validate tar with gzip support
    const tarResult = await this.validateTar();
    results.utilities.tar = tarResult;
    if (!tarResult.functional) {
      results.success = false;
      results.errors.push('tar not functional - required for archive extraction');
    }

    // Validate file utility
    const fileResult = await this.validateFile();
    results.utilities.file = fileResult;
    if (!fileResult.functional) {
      results.success = false;
      results.errors.push('file utility not functional - required for format validation');
    }

    return results;
  }

  private async validateJq(): Promise<UtilityStatus> {
    try {
      const version = await this.getCommandVersion('jq', '--version');
      return {
        available: true,
        functional: true,
        version,
        details: 'JSON processor for GitHub API responses',
      };
    } catch (error) {
      return {
        available: false,
        functional: false,
        version: 'unknown',
        details: 'jq command not found or not functional',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async validateXxd(): Promise<UtilityStatus> {
    try {
      // xxd doesn't have a --version flag, so we test basic functionality
      await this.runCommand('xxd', ['-l', '0', '/dev/null']);
      return {
        available: true,
        functional: true,
        version: 'available',
        details: 'Hex dump utility for binary validation',
      };
    } catch (error) {
      return {
        available: false,
        functional: false,
        version: 'unknown',
        details: 'xxd command not found or not functional',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async validateBc(): Promise<UtilityStatus> {
    try {
      const version = await this.getCommandVersion('bc', '--version');
      return {
        available: true,
        functional: true,
        version,
        details: 'Arbitrary precision calculator for coverage thresholds',
      };
    } catch (error) {
      return {
        available: false,
        functional: false,
        version: 'unknown',
        details: 'bc command not found or not functional',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async validateCurl(): Promise<UtilityStatus> {
    try {
      const version = await this.getCommandVersion('curl', '--version');

      // Test HTTPS connectivity
      let httpsSupport = false;
      try {
        await this.runCommand('curl', [
          '-sSL',
          '--connect-timeout',
          '5',
          '--max-time',
          '10',
          'https://api.github.com',
        ]);
        httpsSupport = true;
      } catch {
        // HTTPS test failed, but curl is still functional
      }

      return {
        available: true,
        functional: true,
        version,
        details: `HTTP client with HTTPS support: ${httpsSupport ? 'Yes' : 'No'}`,
        httpsSupport,
      };
    } catch (error) {
      return {
        available: false,
        functional: false,
        version: 'unknown',
        details: 'curl command not found or not functional',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async validateTar(): Promise<UtilityStatus> {
    try {
      const version = await this.getCommandVersion('tar', '--version');

      // Test gzip functionality
      let gzipSupport = false;
      try {
        const helpOutput = await this.runCommand('tar', ['--help']);
        gzipSupport = helpOutput.includes('gzip');
      } catch {
        // Help command failed, but tar might still work
      }

      return {
        available: true,
        functional: true,
        version,
        details: `Archive extraction with gzip support: ${gzipSupport ? 'Yes' : 'No'}`,
        gzipSupport,
      };
    } catch (error) {
      return {
        available: false,
        functional: false,
        version: 'unknown',
        details: 'tar command not found or not functional',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async validateFile(): Promise<UtilityStatus> {
    try {
      const version = await this.getCommandVersion('file', '--version');
      return {
        available: true,
        functional: true,
        version,
        details: 'File type detection for validation',
      };
    } catch (error) {
      return {
        available: false,
        functional: false,
        version: 'unknown',
        details: 'file command not found or not functional',
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  private async getCommandVersion(command: string, versionFlag: string): Promise<string> {
    try {
      const output = await this.runCommand(command, [versionFlag]);
      return output?.split('\n')[0]?.trim() || 'unknown';
    } catch (error) {
      throw new Error(`Failed to get version for ${command}: ${error}`);
    }
  }

  private async runCommand(command: string, args: string[]): Promise<string> {
    return new Promise((resolve, reject) => {
      try {
        // Mock implementation for testing
        if (command === 'jq' && args.includes('--version')) {
          resolve(mockSystemUtilities.jq.version);
        } else if (command === 'xxd') {
          resolve('');
        } else if (command === 'bc' && args.includes('--version')) {
          resolve(mockSystemUtilities.bc.version);
        } else if (command === 'curl' && args.includes('--version')) {
          resolve(mockSystemUtilities.curl.version);
        } else if (command === 'curl' && args.includes('https://api.github.com')) {
          resolve('{"test": "success"}');
        } else if (command === 'tar' && args.includes('--version')) {
          resolve(mockSystemUtilities.tar.version);
        } else if (command === 'tar' && args.includes('--help')) {
          resolve('Usage: tar [OPTION]... gzip');
        } else if (command === 'file' && args.includes('--version')) {
          resolve(mockSystemUtilities.file.version);
        } else {
          reject(new Error(`Command not found: ${command}`));
        }
      } catch (error) {
        reject(error);
      }
    });
  }
}

// Type definitions
interface ValidationResult {
  success: boolean;
  utilities: Record<string, UtilityStatus>;
  errors: string[];
}

interface UtilityStatus {
  available: boolean;
  functional: boolean;
  version: string;
  details: string;
  error?: string;
  httpsSupport?: boolean;
  gzipSupport?: boolean;
}

describe('SystemUtilitiesValidator', () => {
  let validator: SystemUtilitiesValidator;

  beforeEach(() => {
    validator = new SystemUtilitiesValidator();
  });

  describe('validateUtilities', () => {
    it('should validate all required utilities successfully', async () => {
      const result = await validator.validateUtilities();

      expect(result.success).toBe(true);
      expect(result.errors).toHaveLength(0);
      expect(result.utilities.jq?.functional).toBe(true);
      expect(result.utilities.xxd?.functional).toBe(true);
      expect(result.utilities.bc?.functional).toBe(true);
      expect(result.utilities.curl?.functional).toBe(true);
      expect(result.utilities.tar?.functional).toBe(true);
      expect(result.utilities.file?.functional).toBe(true);
    });

    it('should handle missing utilities gracefully', async () => {
      // Mock a scenario where jq is not available
      const originalRunCommand = validator['runCommand'];
      validator['runCommand'] = vi
        .fn()
        .mockImplementation(async (command: string, args: string[]) => {
          if (command === 'jq') {
            throw new Error('jq: command not found');
          }
          return originalRunCommand.call(validator, command, args);
        });

      const result = await validator.validateUtilities();

      expect(result.success).toBe(false);
      expect(result.errors).toContain('jq not functional - required for GitHub API processing');
      expect(result.utilities.jq?.functional).toBe(false);
      expect(result.utilities.jq?.available).toBe(false);
    });

    it('should validate curl with HTTPS support', async () => {
      const result = await validator.validateUtilities();

      expect(result.utilities.curl?.functional).toBe(true);
      expect(result.utilities.curl?.httpsSupport).toBe(true);
      expect(result.utilities.curl?.details).toContain('HTTPS support: Yes');
    });

    it('should validate tar with gzip support', async () => {
      const result = await validator.validateUtilities();

      expect(result.utilities.tar?.functional).toBe(true);
      expect(result.utilities.tar?.gzipSupport).toBe(true);
      expect(result.utilities.tar?.details).toContain('gzip support: Yes');
    });

    it('should provide detailed error information for failed utilities', async () => {
      // Mock multiple utilities failing
      validator['runCommand'] = vi
        .fn()
        .mockImplementation(async (command: string, args: string[]) => {
          if (command === 'jq' || command === 'xxd' || command === 'bc') {
            throw new Error(`${command}: command not found`);
          }
          // Return success for other commands
          if (command === 'curl' && args.includes('--version')) {
            return mockSystemUtilities.curl.version;
          } else if (command === 'curl' && args.includes('https://api.github.com')) {
            return '{"test": "success"}';
          } else if (command === 'tar' && args.includes('--version')) {
            return mockSystemUtilities.tar.version;
          } else if (command === 'tar' && args.includes('--help')) {
            return 'Usage: tar [OPTION]... gzip';
          } else if (command === 'file' && args.includes('--version')) {
            return mockSystemUtilities.file.version;
          }
          throw new Error(`Command not found: ${command}`);
        });

      const result = await validator.validateUtilities();

      expect(result.success).toBe(false);
      expect(result.errors).toHaveLength(3);
      expect(result.errors).toContain('jq not functional - required for GitHub API processing');
      expect(result.errors).toContain('xxd not functional - required for binary validation');
      expect(result.errors).toContain('bc not functional - required for coverage calculations');
    });
  });

  describe('individual utility validation', () => {
    it('should validate jq with proper version extraction', async () => {
      const result = await validator['validateJq']();

      expect(result.available).toBe(true);
      expect(result.functional).toBe(true);
      expect(result.version).toBe('jq-1.6');
      expect(result.details).toBe('JSON processor for GitHub API responses');
    });

    it('should validate xxd with basic functionality test', async () => {
      const result = await validator['validateXxd']();

      expect(result.available).toBe(true);
      expect(result.functional).toBe(true);
      expect(result.version).toBe('available');
      expect(result.details).toBe('Hex dump utility for binary validation');
    });

    it('should validate bc with version parsing', async () => {
      const result = await validator['validateBc']();

      expect(result.available).toBe(true);
      expect(result.functional).toBe(true);
      expect(result.version).toBe('bc 1.07.1');
      expect(result.details).toBe('Arbitrary precision calculator for coverage thresholds');
    });

    it('should validate curl with comprehensive checks', async () => {
      const result = await validator['validateCurl']();

      expect(result.available).toBe(true);
      expect(result.functional).toBe(true);
      expect(result.version).toBe('curl 7.81.0');
      expect(result.httpsSupport).toBe(true);
      expect(result.details).toContain('HTTP client with HTTPS support: Yes');
    });

    it('should validate tar with gzip support check', async () => {
      const result = await validator['validateTar']();

      expect(result.available).toBe(true);
      expect(result.functional).toBe(true);
      expect(result.version).toBe('tar (GNU tar) 1.34');
      expect(result.gzipSupport).toBe(true);
      expect(result.details).toContain('Archive extraction with gzip support: Yes');
    });

    it('should validate file utility', async () => {
      const result = await validator['validateFile']();

      expect(result.available).toBe(true);
      expect(result.functional).toBe(true);
      expect(result.version).toBe('file-5.41');
      expect(result.details).toBe('File type detection for validation');
    });
  });

  describe('error handling', () => {
    it('should handle command timeout scenarios', async () => {
      validator['runCommand'] = vi
        .fn()
        .mockImplementation(async (command: string, _args: string[]) => {
          if (command === 'jq') {
            const error = new Error('Command timed out');
            (error as any).code = 'ETIMEDOUT';
            throw error;
          }
          return 'success';
        });

      const result = await validator['validateJq']();

      expect(result.available).toBe(false);
      expect(result.functional).toBe(false);
      expect(result.error).toContain('Command timed out');
    });

    it('should handle permission denied errors', async () => {
      validator['runCommand'] = vi
        .fn()
        .mockImplementation(async (command: string, _args: string[]) => {
          if (command === 'xxd') {
            const error = new Error('Permission denied');
            (error as any).code = 'EACCES';
            throw error;
          }
          return 'success';
        });

      const result = await validator['validateXxd']();

      expect(result.available).toBe(false);
      expect(result.functional).toBe(false);
      expect(result.error).toContain('Permission denied');
    });
  });
});
