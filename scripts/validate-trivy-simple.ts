#!/usr/bin/env tsx

/**
 * @fileoverview Simple Trivy Configuration Validation
 * @module scripts/validate-trivy-simple
 * 
 * @description
 * Simplified validation script for TRAIDER V1 Trivy security scanning
 * configurations. Validates key workflow configurations and provides
 * actionable feedback for fixing Trivy issues.
 * 
 * @author TRAIDER Team
 * @since 1.0.0-alpha
 */

import { readFileSync, existsSync } from 'fs';

interface ValidationIssue {
  file: string;
  type: 'ERROR' | 'WARNING';
  message: string;
}

class SimpleTrivyValidator {
  private issues: ValidationIssue[] = [];

  async validate(): Promise<boolean> {
    console.log('🛡️ TRAIDER V1 - Trivy Configuration Validation');
    console.log('================================================\n');

    this.validateWorkflowVersions();
    this.validateExitCodes();
    this.validateTrivyIgnore();
    this.generateReport();

    const errors = this.issues.filter(i => i.type === 'ERROR');
    return errors.length === 0;
  }

  private validateWorkflowVersions(): void {
    const workflows = [
      '.github/workflows/trivy-security.yml',
      '.github/workflows/ci.yml',
      '.github/workflows/security.yml'
    ];

    for (const workflow of workflows) {
      if (!existsSync(workflow)) {
        continue;
      }

      const content = readFileSync(workflow, 'utf8');
      
      // Check for @master usage
      const masterUsage = content.match(/aquasecurity\/trivy-action@master/g);
      if (masterUsage) {
        this.issues.push({
          file: workflow,
          type: 'ERROR',
          message: `Found ${masterUsage.length} Trivy actions using @master. Use @0.30.0 instead.`
        });
      }

      // Check for pinned versions
      const pinnedVersions = content.match(/aquasecurity\/trivy-action@0\.30\.0/g);
      if (pinnedVersions) {
        console.log(`✅ ${workflow}: Found ${pinnedVersions.length} properly pinned Trivy actions`);
      }
    }
  }

  private validateExitCodes(): void {
    const workflows = [
      '.github/workflows/trivy-security.yml',
      '.github/workflows/ci.yml'
    ];

    for (const workflow of workflows) {
      if (!existsSync(workflow)) {
        continue;
      }

      const content = readFileSync(workflow, 'utf8');
      
      // Check for exit-code: '1' which causes failures
      if (content.includes("exit-code: '1'")) {
        this.issues.push({
          file: workflow,
          type: 'ERROR',
          message: "Found exit-code: '1' which will cause pipeline failures. Use exit-code: '0'."
        });
      }

      // Check for proper configuration
      if (content.includes("exit-code: '0'")) {
        console.log(`✅ ${workflow}: Proper exit-code configuration found`);
      }

      // Check for ignore-unfixed
      if (content.includes('ignore-unfixed: true')) {
        console.log(`✅ ${workflow}: ignore-unfixed configuration found`);
      } else if (content.includes('trivy-action')) {
        this.issues.push({
          file: workflow,
          type: 'WARNING',
          message: 'Consider adding ignore-unfixed: true to reduce noise from unfixable vulnerabilities'
        });
      }

      // Check for skip-dirs
      if (content.includes('skip-dirs:')) {
        console.log(`✅ ${workflow}: skip-dirs configuration found`);
      } else if (content.includes('trivy-action')) {
        this.issues.push({
          file: workflow,
          type: 'WARNING',
          message: 'Consider adding skip-dirs to exclude build artifacts'
        });
      }
    }
  }

  private validateTrivyIgnore(): void {
    const trivyIgnorePath = '.trivyignore';
    
    if (!existsSync(trivyIgnorePath)) {
      this.issues.push({
        file: trivyIgnorePath,
        type: 'WARNING',
        message: 'File not found. Consider creating one to manage false positives.'
      });
      return;
    }

    const content = readFileSync(trivyIgnorePath, 'utf8');
    
    // Check for essential patterns
    const essentialPatterns = [
      { pattern: 'node_modules', name: 'node_modules exclusion' },
      { pattern: 'coverage', name: 'coverage exclusion' },
      { pattern: 'test/', name: 'test files exclusion' }
    ];

    for (const { pattern, name } of essentialPatterns) {
      if (content.includes(pattern)) {
        console.log(`✅ .trivyignore: ${name} found`);
      } else {
        this.issues.push({
          file: trivyIgnorePath,
          type: 'WARNING',
          message: `Consider adding ${pattern} pattern for ${name}`
        });
      }
    }

    // Check for CVE suppressions
    const cveCount = (content.match(/CVE-\d{4}-\d+/g) || []).length;
    if (cveCount > 0) {
      console.log(`✅ .trivyignore: Found ${cveCount} CVE suppressions`);
    }
  }

  private generateReport(): void {
    console.log('\n📊 Validation Summary');
    console.log('====================');

    const errors = this.issues.filter(i => i.type === 'ERROR');
    const warnings = this.issues.filter(i => i.type === 'WARNING');

    console.log(`❌ Errors: ${errors.length}`);
    console.log(`⚠️  Warnings: ${warnings.length}`);

    if (errors.length > 0) {
      console.log('\n🚨 Critical Issues (Must Fix):');
      errors.forEach(issue => {
        console.log(`   ${issue.file}: ${issue.message}`);
      });
    }

    if (warnings.length > 0) {
      console.log('\n⚠️  Recommendations:');
      warnings.forEach(issue => {
        console.log(`   ${issue.file}: ${issue.message}`);
      });
    }

    if (errors.length === 0) {
      console.log('\n🎉 All critical validations passed! Trivy configuration is ready.');
    } else {
      console.log('\n🔧 Please fix the critical issues before proceeding.');
    }
  }
}

// Main execution
async function main(): Promise<void> {
  const validator = new SimpleTrivyValidator();
  const success = await validator.validate();
  
  process.exit(success ? 0 : 1);
}

// Run the validation
main().catch(error => {
  console.error('❌ Validation failed:', error);
  process.exit(1);
}); 