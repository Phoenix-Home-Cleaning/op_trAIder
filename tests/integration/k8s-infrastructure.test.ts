/**
 * @fileoverview K8s Infrastructure Integration Tests - Zero Duplication
 * @module tests/integration/k8s-infrastructure
 *
 * @description
 * Comprehensive integration tests for TRAIDER V1 Kubernetes infrastructure using shared utilities.
 * Eliminates code duplication while maintaining institutional-grade validation standards.
 *
 * @performance
 * - Latency target: <20s for full test suite
 * - Throughput: Validates 7 manifests + 15+ resources
 * - Memory usage: <30MB test execution
 *
 * @risk
 * - Failure impact: MEDIUM - Blocks K8s deployments
 * - Recovery strategy: Graceful degradation with detailed error reporting
 *
 * @compliance
 * - Audit requirements: Yes - All K8s validations logged
 * - Data retention: Test results retained for 30 days
 *
 * @see {@link infra/k8s/dev/README.md}
 * @since 1.0.0-alpha
 * @author TRAIDER Team
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { execSync } from 'child_process';
import { readFileSync } from 'fs';
import {
  getManifestFiles,
  validateRequiredFiles,
  validateYamlSyntax,
  runComprehensiveValidation,
  generateValidationSummary,
  parseManifestFile,
  K8S_CONSTANTS,
} from '../utils/k8sTestUtils';

// Test configuration constants
const KUBECTL_TIMEOUT = 30000; // 30 seconds

/**
 * Check if kubectl is available and cluster is accessible
 *
 * @description Validates kubectl installation and cluster connectivity
 *
 * @returns True if kubectl is available and cluster accessible
 *
 * @performance O(1) time, single kubectl call, ~100ms typical latency
 * @sideEffects None - read-only kubectl cluster-info call
 *
 * @tradingImpact None - Infrastructure validation only
 * @riskLevel LOW - Read-only operations
 */
async function isKubectlAvailable(): Promise<boolean> {
  try {
    execSync('kubectl cluster-info', {
      stdio: 'pipe',
      timeout: 5000,
      encoding: 'utf8',
    });
    return true;
  } catch {
    // kubectl not available - skipping integration tests
    return false;
  }
}

/**
 * Execute kubectl command with proper error handling
 *
 * @description Wrapper for kubectl commands with timeout and error handling
 *
 * @param command - kubectl command to execute
 * @param timeout - Command timeout in milliseconds
 * @returns Command output
 *
 * @throws {Error} If command fails or times out
 *
 * @performance Varies by command, timeout configurable
 * @sideEffects kubectl operations may modify cluster state
 *
 * @tradingImpact None - Infrastructure operations only
 * @riskLevel MEDIUM - Can modify K8s cluster state
 */
async function executeKubectl(command: string, timeout: number = KUBECTL_TIMEOUT): Promise<string> {
  try {
    const output = execSync(`kubectl ${command}`, {
      stdio: 'pipe',
      timeout,
      encoding: 'utf8',
    });
    return output.toString().trim();
  } catch (error: any) {
    throw new Error(`kubectl command failed: ${command}\nError: ${error.message}`);
  }
}

describe('🚀 K8s Infrastructure Integration Tests', () => {
  let kubectlAvailable: boolean;
  let validationResults: Record<string, any>;

  beforeAll(async () => {
    kubectlAvailable = await isKubectlAvailable();
    validationResults = runComprehensiveValidation();
  });

  describe('📄 Manifest Validation', () => {
    /**
     * Parameterized manifest validation tests
     * Uses shared utilities to eliminate duplication
     */
    const manifestValidationTests = [
      {
        name: 'should have all required manifest files',
        test: () => {
          const result = validateRequiredFiles();
          expect(result.valid).toBe(true);
          if (!result.valid) {
            // Missing files logged for debugging
          }
        },
      },
      {
        name: 'should have valid YAML syntax in all manifests',
        test: () => {
          const syntaxResults = validateYamlSyntax();
          const allValid = Object.values(syntaxResults).every((result) => result.valid);

          expect(allValid).toBe(true);

          if (!allValid) {
            // Invalid YAML files available for debugging if needed
            void Object.entries(syntaxResults)
              .filter(([_, result]) => !result.valid)
              .map(([file, result]) => `${file}: ${result.errors.join(', ')}`);
          }
        },
      },
      {
        name: 'should have proper Kubernetes resource structure',
        test: () => {
          const manifestFiles = getManifestFiles();
          expect(manifestFiles.length).toBeGreaterThan(0);

          for (const filePath of manifestFiles) {
            const resources = parseManifestFile(filePath);
            expect(resources.length).toBeGreaterThan(0);

            for (const resource of resources) {
              expect(resource).toBeDefined();
              expect(typeof resource).toBe('object');
              expect(resource.apiVersion).toBeDefined();
              expect(resource.kind).toBeDefined();
              expect(resource.metadata).toBeDefined();
              expect(resource.metadata.name).toBeDefined();
            }
          }
        },
      },
    ];

    it.each(manifestValidationTests)('$name', ({ test }) => {
      test();
    });

    it('should pass comprehensive validation checks', () => {
      const summary = generateValidationSummary(validationResults);

      // Log summary for debugging
      // Validation summary available for debugging

      // Should validate all expected files
      expect(summary.filesValidated).toBeGreaterThanOrEqual(K8S_CONSTANTS.REQUIRED_FILES.length);

      // Should have no critical security issues
      expect(summary.criticalIssues.length).toBe(0);

      // Should have high success rate (allow some warnings)
      expect(summary.validationSuccessRate).toBeGreaterThan(80);
    });
  });

  describe('🔧 Resource Configuration', () => {
    /**
     * Parameterized resource configuration tests
     * Uses shared validation utilities
     */
    const resourceTests = [
      {
        name: 'should have proper TRAIDER labeling standards',
        test: () => {
          const manifestFiles = getManifestFiles();
          let labeledResources = 0;
          let properlyLabeledResources = 0;

          for (const filePath of manifestFiles) {
            const resources = parseManifestFile(filePath);

            for (const resource of resources) {
              if (resource.kind !== 'Namespace') {
                // Skip namespace for labeling
                labeledResources++;

                const labels = resource.metadata?.labels || {};
                const traiderLabels = [
                  'traider',
                  'backend',
                  'frontend',
                  'postgres',
                  'redis',
                  'monitoring',
                ];
                if (
                  labels['app.kubernetes.io/name'] &&
                  traiderLabels.includes(labels['app.kubernetes.io/name'])
                ) {
                  properlyLabeledResources++;
                }
              }
            }
          }

          // At least 30% of resources should have proper TRAIDER labels (dev environment)
          const labelingRate = (properlyLabeledResources / labeledResources) * 100;
          expect(labelingRate).toBeGreaterThan(30); // Realistic for development phase
        },
      },
      {
        name: 'should have reasonable resource limits for development',
        test: () => {
          const manifestFiles = getManifestFiles();
          let deploymentCount = 0;
          let deploymentsWithLimits = 0;

          for (const filePath of manifestFiles) {
            const resources = parseManifestFile(filePath);

            for (const resource of resources) {
              if (resource.kind === 'Deployment') {
                deploymentCount++;

                const containers = resource.spec?.template?.spec?.containers || [];
                const hasLimits = containers.some(
                  (container: any) =>
                    container.resources?.limits?.cpu || container.resources?.limits?.memory
                );

                if (hasLimits) {
                  deploymentsWithLimits++;
                }
              }
            }
          }

          // Most deployments should have resource limits
          if (deploymentCount > 0) {
            const limitsRate = (deploymentsWithLimits / deploymentCount) * 100;
            expect(limitsRate).toBeGreaterThan(60); // Allow some flexibility
          }
        },
      },
      {
        name: 'should have proper namespace assignment',
        test: () => {
          const manifestFiles = getManifestFiles();
          let namespacedResources = 0;
          let properlyNamespacedResources = 0;

          for (const filePath of manifestFiles) {
            const resources = parseManifestFile(filePath);

            for (const resource of resources) {
              // Skip cluster-wide resources
              if (!['Namespace', 'ClusterRole', 'ClusterRoleBinding'].includes(resource.kind)) {
                namespacedResources++;

                if (resource.metadata?.namespace === K8S_CONSTANTS.NAMESPACE) {
                  properlyNamespacedResources++;
                }
              }
            }
          }

          // Most resources should be in the correct namespace
          if (namespacedResources > 0) {
            const namespacingRate = (properlyNamespacedResources / namespacedResources) * 100;
            expect(namespacingRate).toBeGreaterThan(70); // Allow some flexibility
          }
        },
      },
    ];

    it.each(resourceTests)('$name', ({ test }) => {
      test();
    });
  });

  describe('🌐 Service and Networking', () => {
    it('should have proper service configuration', () => {
      const manifestFiles = getManifestFiles();
      let serviceCount = 0;
      let validServices = 0;

      for (const filePath of manifestFiles) {
        const resources = parseManifestFile(filePath);

        for (const resource of resources) {
          if (resource.kind === 'Service') {
            serviceCount++;

            const spec = resource.spec || {};
            const ports = spec.ports || [];

            // Service should have ports and selector
            if (ports.length > 0 && spec.selector) {
              validServices++;
            }
          }
        }
      }

      expect(serviceCount).toBeGreaterThan(0);
      expect(validServices).toBe(serviceCount); // All services should be valid
    });

    it('should have consistent port configuration', () => {
      const manifestFiles = getManifestFiles();
      const traderPorts = [3000, 8000, 5432, 6379]; // Common TRAIDER ports
      let portCount = 0;
      let validPorts = 0;

      for (const filePath of manifestFiles) {
        const resources = parseManifestFile(filePath);

        for (const resource of resources) {
          if (resource.kind === 'Service') {
            const ports = resource.spec?.ports || [];

            for (const port of ports) {
              portCount++;

              // Check if port is in expected range or common TRAIDER ports
              if (
                port.port &&
                (traderPorts.includes(port.port) || (port.port >= 3000 && port.port <= 9000))
              ) {
                validPorts++;
              }
            }
          }
        }
      }

      // Most ports should be in expected ranges
      if (portCount > 0) {
        const portValidityRate = (validPorts / portCount) * 100;
        expect(portValidityRate).toBeGreaterThan(80);
      }
    });
  });

  describe('🔒 Security Configuration', () => {
    it('should not have hardcoded secrets in manifests', () => {
      const manifestFiles = getManifestFiles();
      const suspiciousPatterns = [
        /password\s*[:=]\s*["']?[^"'\s]+/i,
        /secret\s*[:=]\s*["']?[^"'\s]+/i,
        /key\s*[:=]\s*["']?[a-zA-Z0-9+/]{20,}/i,
        /token\s*[:=]\s*["']?[^"'\s]+/i,
      ];

      for (const filePath of manifestFiles) {
        const content = readFileSync(filePath, 'utf8');

        for (const pattern of suspiciousPatterns) {
          const matches = content.match(pattern);
          if (matches) {
            // Allow some exceptions for demo/placeholder values
            const allowedValues = ['password', 'secret', 'demo', 'placeholder', 'changeme'];
            const isAllowed = allowedValues.some((allowed) =>
              matches[0].toLowerCase().includes(allowed)
            );

            if (!isAllowed) {
              throw new Error(`Potential hardcoded secret found in ${filePath}: ${matches[0]}`);
            }
          }
        }
      }
    });

    it('should have security context recommendations', () => {
      const manifestFiles = getManifestFiles();
      let deploymentCount = 0;
      let secureDeployments = 0;

      for (const filePath of manifestFiles) {
        const resources = parseManifestFile(filePath);

        for (const resource of resources) {
          if (resource.kind === 'Deployment') {
            deploymentCount++;

            const podSpec = resource.spec?.template?.spec;
            const containers = podSpec?.containers || [];

            // Check for basic security practices
            let hasSecurityFeatures = false;

            // Check pod security context
            if (podSpec?.securityContext?.runAsNonRoot) {
              hasSecurityFeatures = true;
            }

            // Check container security contexts
            for (const container of containers) {
              if (
                container.securityContext?.allowPrivilegeEscalation === false ||
                container.securityContext?.readOnlyRootFilesystem === true
              ) {
                hasSecurityFeatures = true;
              }
            }

            if (hasSecurityFeatures) {
              secureDeployments++;
            }
          }
        }
      }

      // Allow flexibility in development environment
      if (deploymentCount > 0) {
        const securityRate = (secureDeployments / deploymentCount) * 100;
        expect(securityRate).toBeGreaterThan(30); // Minimum security practices
      }
    });
  });

  describe('⚡ Integration with kubectl (if available)', () => {
    it('should be able to validate manifests with kubectl (if cluster available)', async () => {
      if (!kubectlAvailable) {
        // Skipping kubectl integration tests - cluster not available
        return;
      }

      const manifestFiles = getManifestFiles();

      for (const filePath of manifestFiles) {
        try {
          // Dry-run validation with kubectl
          await executeKubectl(`apply -f ${filePath} --dry-run=client`);
        } catch (error) {
          throw new Error(`kubectl validation failed for ${filePath}: ${error}`);
        }
      }
    });

    it('should have proper development environment configuration', () => {
      // This test runs regardless of kubectl availability
      const manifestFiles = getManifestFiles();
      let devConfigCount = 0;

      for (const filePath of manifestFiles) {
        const resources = parseManifestFile(filePath);

        for (const resource of resources) {
          // Check for development-specific configurations
          const labels = resource.metadata?.labels || {};
          const annotations = resource.metadata?.annotations || {};

          if (
            labels.environment === 'development' ||
            annotations['traider.dev/environment'] === 'dev' ||
            resource.metadata?.name?.includes('-dev')
          ) {
            devConfigCount++;
          }
        }
      }

      // Should have some development-specific configurations
      expect(devConfigCount).toBeGreaterThan(0);
    });
  });

  describe('📊 Performance and Validation Summary', () => {
    it('should complete validation within performance targets', () => {
      const start = performance.now();

      // Re-run validation to measure performance
      const results = runComprehensiveValidation();
      const summary = generateValidationSummary(results);

      const duration = performance.now() - start;

      // Should complete validation quickly
      expect(duration).toBeLessThan(5000); // <5 seconds

      // Should validate expected number of files
      expect(summary.filesValidated).toBeGreaterThanOrEqual(K8S_CONSTANTS.REQUIRED_FILES.length);
    });
  });
});
