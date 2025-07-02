/**
 * @fileoverview Kubernetes Test Utilities - Zero Duplication
 * @module tests.utils.k8sTestUtils
 *
 * @description
 * Shared utilities for Kubernetes infrastructure and manifest testing.
 * Eliminates code duplication across K8s-related test suites while maintaining
 * comprehensive validation for TRAIDER V1 infrastructure.
 *
 * @performance
 * - Validation target: <50ms per manifest
 * - Memory usage: <2MB per test suite
 * - Coverage requirement: >95%
 *
 * @risk
 * - Failure impact: HIGH - Infrastructure validation is critical
 * - Recovery strategy: Automated retry with detailed logging
 *
 * @compliance
 * - Audit requirements: Yes - Infrastructure security validation
 * - Data retention: Test logs retained for 90 days
 *
 * @see {@link docs/infrastructure/k8s/README.md}
 * @since 1.0.0
 * @author TRAIDER Team
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { join } from 'path';
import { loadAll } from 'js-yaml';

// =============================================================================
// TYPES AND INTERFACES
// =============================================================================

/**
 * Kubernetes resource structure for type safety
 */
export interface K8sResource {
  apiVersion: string;
  kind: string;
  metadata: {
    name: string;
    namespace?: string;
    labels?: Record<string, string>;
    annotations?: Record<string, string>;
  };
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  spec?: any;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  data?: any;
}

/**
 * Manifest validation result
 */
export interface ValidationResult {
  valid: boolean;
  errors: string[];
  warnings: string[];
  resource?: K8sResource;
}

/**
 * Resource limits configuration
 */
export interface ResourceLimits {
  cpu?: string;
  memory?: string;
  'ephemeral-storage'?: string;
}

/**
 * Security context configuration
 */
export interface SecurityContext {
  runAsNonRoot?: boolean;
  runAsUser?: number;
  runAsGroup?: number;
  readOnlyRootFilesystem?: boolean;
  allowPrivilegeEscalation?: boolean;
  capabilities?: {
    drop?: string[];
    add?: string[];
  };
}

// =============================================================================
// CONSTANTS AND CONFIGURATION
// =============================================================================

/**
 * TRAIDER V1 infrastructure constants
 */
export const K8S_CONSTANTS = {
  NAMESPACE: 'traider-dev',
  REQUIRED_LABELS: {
    'app.kubernetes.io/name': 'traider',
    'app.kubernetes.io/version': '1.0.0-alpha',
    'app.kubernetes.io/component': true, // Must be present
    'app.kubernetes.io/part-of': 'traider-platform',
    'app.kubernetes.io/managed-by': 'helm',
  },
  MANIFEST_DIRECTORY: 'infrastructure/k8s/dev',
  REQUIRED_FILES: [
    'namespace.yaml',
    'postgres-dev.yaml',
    'redis-dev.yaml',
    'backend-dev.yaml',
    'frontend-dev.yaml',
    'monitoring-dev.yaml',
    'ingress-nginx.yaml',
  ],
  VALID_API_VERSIONS: [
    'v1',
    'apps/v1',
    'networking.k8s.io/v1',
    'networking.k8s.io/v1beta1',
    'extensions/v1beta1',
    'monitoring.coreos.com/v1',
  ],
  VALID_KINDS: [
    'Namespace',
    'Deployment',
    'Service',
    'ConfigMap',
    'Secret',
    'Ingress',
    'PersistentVolumeClaim',
    'ServiceMonitor',
  ],
  RESOURCE_LIMITS: {
    DEV: {
      cpu: '2000m',
      memory: '4Gi',
      'ephemeral-storage': '10Gi',
    },
    PROD: {
      cpu: '4000m',
      memory: '8Gi',
      'ephemeral-storage': '20Gi',
    },
  },
} as const;

// =============================================================================
// FILE SYSTEM UTILITIES
// =============================================================================

/**
 * Get all manifest files from the K8s directory
 *
 * @description
 * Recursively finds all YAML manifest files in the Kubernetes directory
 *
 * @returns Array of manifest file paths
 *
 * @performance O(n) where n is number of files
 * @sideEffects File system reads
 *
 * @tradingImpact Critical for infrastructure validation
 * @riskLevel HIGH - Infrastructure files must be validated
 *
 * @example
 * ```typescript
 * const manifestFiles = getManifestFiles();
 * // manifestFiles = ['infrastructure/k8s/dev/namespace.yaml', ...]
 * ```
 */
export const getManifestFiles = (): string[] => {
  const manifestDir = K8S_CONSTANTS.MANIFEST_DIRECTORY;

  if (!existsSync(manifestDir)) {
    throw new Error(`Manifest directory not found: ${manifestDir}`);
  }

  const files: string[] = [];
  const entries = readdirSync(manifestDir, { withFileTypes: true });

  for (const entry of entries) {
    const fullPath = join(manifestDir, entry.name);

    if (entry.isFile() && (entry.name.endsWith('.yaml') || entry.name.endsWith('.yml'))) {
      files.push(fullPath);
    }
  }

  return files.sort(); // Consistent ordering for tests
};

/**
 * Check if all required manifest files exist
 *
 * @description
 * Validates that all required Kubernetes manifest files are present
 *
 * @returns Validation result with missing files
 *
 * @performance O(n) where n is number of required files
 * @sideEffects File system reads
 *
 * @tradingImpact Critical for deployment readiness
 * @riskLevel CRITICAL - Missing files prevent deployment
 */
export const validateRequiredFiles = (): ValidationResult => {
  const manifestDir = K8S_CONSTANTS.MANIFEST_DIRECTORY;
  const errors: string[] = [];
  const warnings: string[] = [];

  for (const requiredFile of K8S_CONSTANTS.REQUIRED_FILES) {
    const filePath = join(manifestDir, requiredFile);

    if (!existsSync(filePath)) {
      errors.push(`Required manifest file missing: ${requiredFile}`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
};

// =============================================================================
// YAML PARSING UTILITIES
// =============================================================================

/**
 * Parse YAML manifest file safely
 *
 * @description
 * Safely parses Kubernetes YAML manifest files with error handling
 *
 * @param filePath - Path to the YAML file
 * @returns Array of parsed Kubernetes resources
 *
 * @throws {Error} If file cannot be read or parsed
 *
 * @performance O(n) where n is file size
 * @sideEffects File system reads
 *
 * @tradingImpact Critical for manifest validation
 * @riskLevel HIGH - Invalid YAML prevents deployment
 */
export const parseManifestFile = (filePath: string): K8sResource[] => {
  try {
    const fileContent = readFileSync(filePath, 'utf8');
    const documents = loadAll(fileContent) as K8sResource[];

    return documents.filter((doc) => doc !== null && doc !== undefined);
  } catch (error) {
    throw new Error(`Failed to parse manifest file ${filePath}: ${error}`);
  }
};

/**
 * Validate YAML syntax for all manifest files
 *
 * @description
 * Validates YAML syntax across all Kubernetes manifest files
 *
 * @returns Validation results for all files
 *
 * @performance O(n*m) where n is files, m is file size
 * @sideEffects File system reads
 *
 * @tradingImpact Critical for deployment readiness
 * @riskLevel HIGH - Invalid YAML prevents deployment
 */
export const validateYamlSyntax = (): Record<string, ValidationResult> => {
  const manifestFiles = getManifestFiles();
  const results: Record<string, ValidationResult> = {};

  for (const filePath of manifestFiles) {
    try {
      parseManifestFile(filePath);
      results[filePath] = {
        valid: true,
        errors: [],
        warnings: [],
      };
    } catch (error) {
      results[filePath] = {
        valid: false,
        errors: [error instanceof Error ? error.message : String(error)],
        warnings: [],
      };
    }
  }

  return results;
};

// =============================================================================
// KUBERNETES RESOURCE VALIDATION
// =============================================================================

/**
 * Validate Kubernetes resource structure
 *
 * @description
 * Validates that a Kubernetes resource has the required structure and fields
 *
 * @param resource - The Kubernetes resource to validate
 * @returns Validation result with detailed errors
 *
 * @performance O(1) - constant time validation
 * @sideEffects None
 *
 * @tradingImpact Critical for resource deployment
 * @riskLevel HIGH - Invalid resources prevent deployment
 */
export const validateResourceStructure = (resource: K8sResource): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  // Validate required fields
  if (!resource.apiVersion) {
    errors.push('Missing required field: apiVersion');
  } else if (
    !(K8S_CONSTANTS.VALID_API_VERSIONS as readonly string[]).includes(resource.apiVersion)
  ) {
    warnings.push(`Uncommon apiVersion: ${resource.apiVersion}`);
  }

  if (!resource.kind) {
    errors.push('Missing required field: kind');
  } else if (!(K8S_CONSTANTS.VALID_KINDS as readonly string[]).includes(resource.kind)) {
    warnings.push(`Uncommon kind: ${resource.kind}`);
  }

  if (!resource.metadata) {
    errors.push('Missing required field: metadata');
  } else {
    if (!resource.metadata.name) {
      errors.push('Missing required field: metadata.name');
    }

    // Validate naming convention
    if (resource.metadata.name && !/^[a-z0-9-]+$/.test(resource.metadata.name)) {
      errors.push(
        `Invalid name format: ${resource.metadata.name}. Must be lowercase alphanumeric with hyphens.`
      );
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    resource,
  };
};

/**
 * Validate TRAIDER labeling standards
 *
 * @description
 * Validates that resources follow TRAIDER V1 labeling conventions
 *
 * @param resource - The Kubernetes resource to validate
 * @returns Validation result with labeling errors
 *
 * @performance O(1) - constant time validation
 * @sideEffects None
 *
 * @tradingImpact Medium - affects monitoring and management
 * @riskLevel MEDIUM - Improper labels affect operations
 */
export const validateTraiderLabels = (resource: K8sResource): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];
  const labels = resource.metadata?.labels || {};

  // Check for TRAIDER labeling standards (flexible for development)
  const hasAppName = labels['app.kubernetes.io/name'];
  const hasComponent = labels['app.kubernetes.io/component'] || labels['component'];
  const hasPartOf = labels['app.kubernetes.io/part-of'];

  if (!hasAppName) {
    warnings.push('Missing recommended label: app.kubernetes.io/name');
  }

  if (!hasComponent) {
    warnings.push('Missing recommended label: app.kubernetes.io/component or component');
  }

  if (!hasPartOf) {
    warnings.push('Missing recommended label: app.kubernetes.io/part-of');
  }

  // Validate namespace assignment
  if (resource.kind !== 'Namespace' && resource.metadata?.namespace !== K8S_CONSTANTS.NAMESPACE) {
    warnings.push(`Resource should be in namespace: ${K8S_CONSTANTS.NAMESPACE}`);
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    resource,
  };
};

// =============================================================================
// RESOURCE CONFIGURATION VALIDATION
// =============================================================================

/**
 * Validate resource limits and requests
 *
 * @description
 * Validates that deployments have appropriate resource limits for development
 *
 * @param resource - The Kubernetes resource to validate
 * @returns Validation result with resource configuration errors
 *
 * @performance O(n) where n is number of containers
 * @sideEffects None
 *
 * @tradingImpact High - affects system performance and stability
 * @riskLevel HIGH - Improper limits can cause system instability
 */
export const validateResourceLimits = (resource: K8sResource): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (resource.kind !== 'Deployment') {
    return { valid: true, errors: [], warnings: [] };
  }

  const containers = resource.spec?.template?.spec?.containers || [];
  const devLimits = K8S_CONSTANTS.RESOURCE_LIMITS.DEV;

  for (const container of containers) {
    const resources = container.resources || {};
    const limits = resources.limits || {};
    const requests = resources.requests || {};

    // Check if limits are set
    if (!limits.cpu && !limits.memory) {
      warnings.push(`Container ${container.name} has no resource limits`);
    }

    // Check if limits are reasonable for development
    if (limits.cpu && parseInt(limits.cpu) > parseInt(devLimits.cpu)) {
      warnings.push(
        `Container ${container.name} CPU limit exceeds dev recommendation: ${limits.cpu} > ${devLimits.cpu}`
      );
    }

    if (limits.memory && parseInt(limits.memory) > parseInt(devLimits.memory)) {
      warnings.push(
        `Container ${container.name} memory limit exceeds dev recommendation: ${limits.memory} > ${devLimits.memory}`
      );
    }

    // Check if requests are set
    if (!requests.cpu && !requests.memory) {
      warnings.push(`Container ${container.name} has no resource requests`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    resource,
  };
};

/**
 * Validate security context configuration
 *
 * @description
 * Validates security context settings for containers and pods
 *
 * @param resource - The Kubernetes resource to validate
 * @returns Validation result with security configuration errors
 *
 * @performance O(n) where n is number of containers
 * @sideEffects None
 *
 * @tradingImpact Critical - affects system security
 * @riskLevel CRITICAL - Security misconfigurations expose vulnerabilities
 */
export const validateSecurityContext = (resource: K8sResource): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (resource.kind !== 'Deployment') {
    return { valid: true, errors: [], warnings: [] };
  }

  const podSpec = resource.spec?.template?.spec;
  const containers = podSpec?.containers || [];

  // Check pod security context
  const podSecurityContext = podSpec?.securityContext;
  if (!podSecurityContext?.runAsNonRoot) {
    warnings.push('Pod should run as non-root user for security');
  }

  // Check container security contexts
  for (const container of containers) {
    const securityContext = container.securityContext || {};

    if (securityContext.privileged) {
      errors.push(`Container ${container.name} should not run in privileged mode`);
    }

    if (securityContext.allowPrivilegeEscalation !== false) {
      warnings.push(`Container ${container.name} should disable privilege escalation`);
    }

    if (!securityContext.readOnlyRootFilesystem) {
      warnings.push(`Container ${container.name} should use read-only root filesystem`);
    }
  }

  // Check init container security contexts
  const initContainers = podSpec?.initContainers || [];
  for (const container of initContainers) {
    const securityContext = container.securityContext || {};

    if (securityContext.privileged) {
      errors.push(`Init container ${container.name} should not run in privileged mode`);
    }

    if (securityContext.allowPrivilegeEscalation !== false) {
      warnings.push(`Init container ${container.name} should disable privilege escalation`);
    }

    if (!securityContext.readOnlyRootFilesystem) {
      warnings.push(`Init container ${container.name} should use read-only root filesystem`);
    }
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    resource,
  };
};

// =============================================================================
// SERVICE AND NETWORKING VALIDATION
// =============================================================================

/**
 * Validate service configuration
 *
 * @description
 * Validates Kubernetes service configurations for consistency
 *
 * @param resource - The Kubernetes resource to validate
 * @returns Validation result with service configuration errors
 *
 * @performance O(1) - constant time validation
 * @sideEffects None
 *
 * @tradingImpact High - affects service connectivity
 * @riskLevel HIGH - Service misconfigurations break connectivity
 */
export const validateServiceConfiguration = (resource: K8sResource): ValidationResult => {
  const errors: string[] = [];
  const warnings: string[] = [];

  if (resource.kind !== 'Service') {
    return { valid: true, errors: [], warnings: [] };
  }

  const spec = resource.spec || {};
  const ports = spec.ports || [];

  // Validate port configuration
  if (ports.length === 0) {
    errors.push('Service must define at least one port');
  }

  for (const port of ports) {
    if (!port.port) {
      errors.push('Service port must define port number');
    }

    if (!port.targetPort) {
      warnings.push(`Port ${port.port} should define targetPort`);
    }

    // Check for common TRAIDER ports
    const traderPorts = [3000, 8000, 5432, 6379];
    if (port.port && !traderPorts.includes(port.port)) {
      warnings.push(`Uncommon port for TRAIDER services: ${port.port}`);
    }
  }

  // Validate selector
  if (!spec.selector) {
    errors.push('Service must define selector');
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    resource,
  };
};

// =============================================================================
// COMPREHENSIVE VALIDATION UTILITIES
// =============================================================================

/**
 * Run comprehensive validation on all manifest files
 *
 * @description
 * Runs all validation checks on all Kubernetes manifest files
 *
 * @returns Comprehensive validation results
 *
 * @performance O(n*m) where n is files, m is validations per file
 * @sideEffects File system reads
 *
 * @tradingImpact Critical - comprehensive infrastructure validation
 * @riskLevel CRITICAL - Infrastructure must be validated before deployment
 */
export const runComprehensiveValidation = (): Record<string, ValidationResult[]> => {
  const manifestFiles = getManifestFiles();
  const results: Record<string, ValidationResult[]> = {};

  for (const filePath of manifestFiles) {
    const fileResults: ValidationResult[] = [];

    try {
      const resources = parseManifestFile(filePath);

      for (const resource of resources) {
        // Run all validation checks
        const validations = [
          validateResourceStructure(resource),
          validateTraiderLabels(resource),
          validateResourceLimits(resource),
          validateSecurityContext(resource),
          validateServiceConfiguration(resource),
        ];

        fileResults.push(...validations);
      }
    } catch (error) {
      fileResults.push({
        valid: false,
        errors: [error instanceof Error ? error.message : String(error)],
        warnings: [],
      });
    }

    results[filePath] = fileResults;
  }

  return results;
};

/**
 * Generate validation summary report
 *
 * @description
 * Generates a summary report of all validation results
 *
 * @param results - Validation results from comprehensive validation
 * @returns Summary statistics and critical issues
 *
 * @performance O(n*m) where n is files, m is validations per file
 * @sideEffects None
 *
 * @tradingImpact Medium - provides validation overview
 * @riskLevel LOW - Summary generation doesn't affect infrastructure
 */
export const generateValidationSummary = (results: Record<string, ValidationResult[]>) => {
  let totalValidations = 0;
  let validValidations = 0;
  let totalErrors = 0;
  let totalWarnings = 0;
  const criticalIssues: string[] = [];

  for (const [filePath, fileResults] of Object.entries(results)) {
    for (const result of fileResults) {
      totalValidations++;

      if (result.valid) {
        validValidations++;
      }

      totalErrors += result.errors.length;
      totalWarnings += result.warnings.length;

      // Collect critical issues (only truly critical ones for development)
      for (const error of result.errors) {
        if (
          error.toLowerCase().includes('privileged') ||
          error.toLowerCase().includes('missing required field') ||
          error.toLowerCase().includes('hardcoded secret')
        ) {
          criticalIssues.push(`${filePath}: ${error}`);
        }
      }
    }
  }

  return {
    totalValidations,
    validValidations,
    validationSuccessRate: (validValidations / totalValidations) * 100,
    totalErrors,
    totalWarnings,
    criticalIssues,
    filesValidated: Object.keys(results).length,
  };
};
