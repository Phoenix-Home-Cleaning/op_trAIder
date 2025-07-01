#!/usr/bin/env tsx

/* eslint-disable no-console */

/**
 * @fileoverview Documentation validation system for TRAIDER V1
 * @module scripts/validate-docs
 * 
 * @description
 * Validates that all public functions have JSDoc comments, API routes are
 * documented, README files exist for modules, example code compiles, and
 * checks for broken links throughout the documentation.
 * 
 * @author TRAIDER Team
 * @since 2025-06-29
 */

import { readFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { glob } from 'glob';
import { execSync } from 'child_process';

interface ValidationResult {
  passed: boolean;
  errors: string[];
  warnings: string[];
  score: number;
}

interface ValidationConfig {
  requireJSDoc: boolean;
  requireAPIDocumentation: boolean;
  requireModuleREADMEs: boolean;
  validateExamples: boolean;
  checkBrokenLinks: boolean;
  excludePatterns: string[];
}

class DocumentationValidator {
  private config: ValidationConfig;
  private projectRoot: string;
  private results: ValidationResult;

  constructor(config: ValidationConfig) {
    this.config = config;
    this.projectRoot = process.cwd();
    this.results = {
      passed: true,
      errors: [],
      warnings: [],
      score: 100
    };
  }

  /**
   * Run all validation checks
   */
  async validate(): Promise<ValidationResult> {
    console.log('🔍 Starting TRAIDER documentation validation...\n');

    try {
      // 1. Check JSDoc coverage
      if (this.config.requireJSDoc) {
        await this.validateJSDocCoverage();
      }

      // 2. Validate API documentation
      if (this.config.requireAPIDocumentation) {
        await this.validateAPIDocumentation();
      }

      // 3. Check module README files
      if (this.config.requireModuleREADMEs) {
        await this.validateModuleREADMEs();
      }

      // 4. Validate example code
      if (this.config.validateExamples) {
        await this.validateExampleCode();
      }

      // 5. Check for broken links
      if (this.config.checkBrokenLinks) {
        await this.validateLinks();
      }

      // Calculate final score
      this.calculateScore();

      // Print results
      this.printResults();

      return this.results;

    } catch (error) {
      console.error('❌ Documentation validation failed:', error);
      this.results.passed = false;
      this.results.errors.push(`Validation failed: ${error}`);
      return this.results;
    }
  }

  /**
   * Validate JSDoc coverage for public functions
   */
  private async validateJSDocCoverage(): Promise<void> {
    console.log('📝 Validating JSDoc coverage...');

    const tsFiles = await glob('**/*.{ts,tsx}', {
      cwd: this.projectRoot,
      ignore: [
        'node_modules/**',
        '.next/**',
        'dist/**',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        ...this.config.excludePatterns
      ]
    });

    let totalFunctions = 0;
    let documentedFunctions = 0;
    const undocumentedFunctions: string[] = [];

    for (const file of tsFiles) {
      const content = readFileSync(join(this.projectRoot, file), 'utf-8');
      const functions = this.extractFunctions(content);
      
      for (const func of functions) {
        totalFunctions++;
        
        if (this.hasJSDocComment(content, func)) {
          documentedFunctions++;
        } else {
          undocumentedFunctions.push(`${file}:${func.name}`);
        }
      }
    }

    const coverage = totalFunctions > 0 ? (documentedFunctions / totalFunctions) * 100 : 100;
    
    if (coverage < 90) {
      this.results.errors.push(
        `JSDoc coverage is ${coverage.toFixed(1)}% (${documentedFunctions}/${totalFunctions}). Required: 90%`
      );
      this.results.passed = false;
    } else if (coverage < 95) {
      this.results.warnings.push(
        `JSDoc coverage is ${coverage.toFixed(1)}%. Consider improving to 95%+`
      );
    }

    if (undocumentedFunctions.length > 0) {
      console.log(`⚠️  Undocumented functions (${undocumentedFunctions.length}):`);
      undocumentedFunctions.slice(0, 10).forEach(func => {
        console.log(`   - ${func}`);
      });
      if (undocumentedFunctions.length > 10) {
        console.log(`   ... and ${undocumentedFunctions.length - 10} more`);
      }
    }

    console.log(`✅ JSDoc coverage: ${coverage.toFixed(1)}%`);
  }

  /**
   * Validate API route documentation
   */
  private async validateAPIDocumentation(): Promise<void> {
    console.log('🔌 Validating API documentation...');

    const apiFiles = await glob('**/route.{ts,js}', {
      cwd: join(this.projectRoot, 'app/api'),
      ignore: ['node_modules/**']
    });

    const undocumentedRoutes: string[] = [];

    for (const file of apiFiles) {
      const content = readFileSync(join(this.projectRoot, 'app/api', file), 'utf-8');
      const httpMethods = this.extractHTTPMethods(content);
      
      for (const method of httpMethods) {
        if (!this.hasAPIDocumentation(content, method)) {
          undocumentedRoutes.push(`${file}:${method}`);
        }
      }
    }

    if (undocumentedRoutes.length > 0) {
      this.results.errors.push(
        `${undocumentedRoutes.length} API routes lack proper documentation`
      );
      this.results.passed = false;
      
      console.log('⚠️  Undocumented API routes:');
      undocumentedRoutes.forEach(route => {
        console.log(`   - ${route}`);
      });
    }

    console.log(`✅ API documentation: ${apiFiles.length - undocumentedRoutes.length}/${apiFiles.length} routes documented`);
  }

  /**
   * Validate module README files
   */
  private async validateModuleREADMEs(): Promise<void> {
    console.log('📚 Validating module README files...');

    const directories = await this.getDirectories('app');
    const missingREADMEs: string[] = [];

    for (const dir of directories) {
      const readmePath = join(this.projectRoot, dir, 'README.md');
      if (!existsSync(readmePath)) {
        missingREADMEs.push(dir);
      }
    }

    if (missingREADMEs.length > 0) {
      this.results.warnings.push(
        `${missingREADMEs.length} directories missing README.md files`
      );
      
      console.log('⚠️  Missing README files:');
      missingREADMEs.forEach(dir => {
        console.log(`   - ${dir}/README.md`);
      });
    }

    console.log(`✅ Module READMEs: ${directories.length - missingREADMEs.length}/${directories.length} present`);
  }

  /**
   * Validate example code compilation
   */
  private async validateExampleCode(): Promise<void> {
    console.log('🧪 Validating example code...');

    const mdFiles = await glob('**/*.md', {
      cwd: this.projectRoot,
      ignore: ['node_modules/**', '.next/**']
    });

    const failedExamples: string[] = [];

    for (const file of mdFiles) {
      const content = readFileSync(join(this.projectRoot, file), 'utf-8');
      const codeBlocks = this.extractCodeBlocks(content);
      
      for (const block of codeBlocks) {
        if (block.language === 'typescript' || block.language === 'javascript') {
          // Skip examples that are clearly for illustration purposes
          if (this.isIllustrationExample(block.code)) {
            continue;
          }

          try {
            // Create temporary file and try to compile
            const tempFile = `/tmp/example-${Date.now()}.ts`;
            const fs = await import('fs');
            fs.writeFileSync(tempFile, block.code);
            
            execSync(`npx tsc --noEmit --skipLibCheck ${tempFile}`, { 
              stdio: 'pipe',
              timeout: 5000 
            });
            
            // Clean up
            fs.unlinkSync(tempFile);
          } catch {
            failedExamples.push(`${file}:${block.line}`);
          }
        }
      }
    }

    if (failedExamples.length > 0) {
      this.results.warnings.push(
        `${failedExamples.length} code examples may have compilation issues`
      );
      
      console.log('⚠️  Failed code examples:');
      failedExamples.forEach(example => {
        console.log(`   - ${example}`);
      });
    }

    console.log(`✅ Example code validation completed`);
  }

  /**
   * Check if code example is for illustration purposes only
   */
  private isIllustrationExample(code: string): boolean {
    // Skip examples with common documentation patterns
    const illustrationPatterns = [
      // Import from non-existent or placeholder modules
      /import.*from\s+['"]\.\/(?:errors|logging|config|utils)/,
      /import.*TradingError/,
      /import.*createLogger/,
      /import.*getConfig/,
      
      // Comments indicating examples
      /\/\/.*example/i,
      /\/\/.*illustration/i,
      /\/\/.*placeholder/i,
      /\/\/.*TODO/i,
      
      // Configuration examples
      /process\.env\./,
      /config\./,
      
      // Partial code snippets
      /\.\.\./,
      /\/\/ Implementation/i,
      /\/\/ Your implementation/i,
      
      // Shell commands and non-TypeScript code
      /npm run/,
      /npx/,
      /yarn/,
      /bash/,
      /curl/,
      
      // Environment variables
      /export\s+\w+=/,
      /DATABASE_URL=/,
      /API_KEY=/,
    ];

    return illustrationPatterns.some(pattern => pattern.test(code));
  }

  /**
   * Validate links in documentation
   */
  private async validateLinks(): Promise<void> {
    console.log('🔗 Validating links...');

    const mdFiles = await glob('**/*.md', {
      cwd: this.projectRoot,
      ignore: ['node_modules/**', '.next/**']
    });

    const brokenLinks: string[] = [];

    for (const file of mdFiles) {
      const content = readFileSync(join(this.projectRoot, file), 'utf-8');
      const links = this.extractLinks(content);
      
      for (const link of links) {
        if (link.startsWith('./') || link.startsWith('../')) {
          // Relative link - check if file exists
          const linkPath = join(dirname(join(this.projectRoot, file)), link);
          if (!existsSync(linkPath)) {
            brokenLinks.push(`${file}: ${link}`);
          }
        }
        // Skip external links for now (would require network requests)
      }
    }

    if (brokenLinks.length > 0) {
      this.results.warnings.push(
        `${brokenLinks.length} potentially broken internal links found`
      );
      
      console.log('⚠️  Potentially broken links:');
      brokenLinks.slice(0, 10).forEach(link => {
        console.log(`   - ${link}`);
      });
      if (brokenLinks.length > 10) {
        console.log(`   ... and ${brokenLinks.length - 10} more`);
      }
    }

    console.log(`✅ Link validation completed`);
  }

  /**
   * Calculate overall documentation score
   */
  private calculateScore(): void {
    let score = 100;
    
    // Deduct points for errors (major issues)
    score -= this.results.errors.length * 10;
    
    // Deduct points for warnings (minor issues)
    score -= this.results.warnings.length * 2;
    
    // Ensure score doesn't go below 0
    this.results.score = Math.max(0, score);
  }

  /**
   * Print validation results
   */
  private printResults(): void {
    console.log('\n📊 Documentation Validation Results');
    console.log('=' .repeat(50));
    
    console.log(`Overall Score: ${this.results.score}/100`);
    console.log(`Status: ${this.results.passed ? '✅ PASSED' : '❌ FAILED'}`);
    
    if (this.results.errors.length > 0) {
      console.log(`\n❌ Errors (${this.results.errors.length}):`);
      this.results.errors.forEach(error => {
        console.log(`   - ${error}`);
      });
    }
    
    if (this.results.warnings.length > 0) {
      console.log(`\n⚠️  Warnings (${this.results.warnings.length}):`);
      this.results.warnings.forEach(warning => {
        console.log(`   - ${warning}`);
      });
    }
    
    if (this.results.passed) {
      console.log('\n🎉 All documentation validation checks passed!');
    } else {
      console.log('\n🔧 Please fix the errors above before proceeding.');
    }
  }

  /**
   * Extract function definitions from TypeScript code
   */
  private extractFunctions(content: string): Array<{ name: string; line: number }> {
    const functions: Array<{ name: string; line: number }> = [];
    const lines = content.split('\n');
    
    // Improved regex to better detect actual functions and exclude variables
    const functionRegex = /(?:export\s+)?(?:async\s+)?function\s+(\w+)|(?:export\s+)?const\s+(\w+)\s*=\s*(?:async\s+)?\(|(?:export\s+default\s+)?(?:async\s+)?function\s+(\w+)/;
    
    lines.forEach((line, index) => {
      const match = line.match(functionRegex);
      if (match) {
        const functionName = match[1] || match[2] || match[3];
        
        // Skip if line is commented out
        if (line.includes('//') || line.includes('/*')) {
          return;
        }
        
        // Skip if it's just a variable assignment (not a function)
        if (match[2] && !line.includes('(') && !line.includes('=>')) {
          return;
        }
        
        // Skip if it's a simple variable assignment like "const x = 5"
        if (match[2] && /=\s*[^(]*;/.test(line) && !line.includes('function') && !line.includes('=>')) {
          return;
        }
        
        if (functionName && functionName.length > 0) {
          functions.push({ name: functionName, line: index + 1 });
        }
      }
    });
    
    return functions;
  }

  /**
   * Check if function has JSDoc comment
   */
  private hasJSDocComment(content: string, func: { name: string; line: number }): boolean {
    const lines = content.split('\n');
    const funcLine = func.line - 1;
    
    // Look for JSDoc comment above the function
    for (let i = funcLine - 1; i >= 0; i--) {
      const line = lines[i]?.trim();
      
      // Skip empty lines
      if (!line || line === '') {
        continue;
      }
      
      // If we found the end of a JSDoc comment, look for the start
      if (line === '*/') {
        continue;
      }
      
      // If this is the start of a JSDoc comment
      if (line.startsWith('/**')) {
        return true;
      }
      
      // If this is a JSDoc line (starts with *)
      if (line.startsWith('*') && !line.startsWith('*/')) {
        continue;
      }
      
      // If this is a single-line comment, continue looking
      if (line.startsWith('//')) {
        continue;
      }
      
      // If we hit any other non-empty line, stop looking
      break;
    }
    
    return false;
  }

  /**
   * Extract HTTP methods from API route file
   */
  private extractHTTPMethods(content: string): string[] {
    const methods: string[] = [];
    const httpMethods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'];
    
    httpMethods.forEach(method => {
      if (content.includes(`export async function ${method}`)) {
        methods.push(method);
      }
    });
    
    return methods;
  }

  /**
   * Check if API method has documentation
   */
  private hasAPIDocumentation(content: string, method: string): boolean {
    // Simplified check for a comment block above the method
    const lines = content.split('\n');
    const methodLine = lines.findIndex(line => line.includes(`export async function ${method}`));

    if (methodLine === -1) {
      return false;
    }
    
    for (let i = methodLine - 1; i >= 0 && i > methodLine - 5; i--) {
      if (lines[i]?.trim().startsWith('/**')) {
        return true;
      }
    }

    return false;
  }

  /**
   * Get all directories in a path
   */
  private async getDirectories(basePath: string): Promise<string[]> {
    const entries = readdirSync(join(this.projectRoot, basePath), { withFileTypes: true });
    const dirs = entries
      .filter(dirent => dirent.isDirectory())
      .map(dirent => join(basePath, dirent.name));

    for (const dir of dirs) {
      if (!this.config.excludePatterns.some(p => dir.includes(p))) {
        dirs.push(...(await this.getDirectories(dir)));
      }
    }

    return dirs;
  }

  /**
   * Extract code blocks from markdown
   */
  private extractCodeBlocks(content: string): Array<{ language: string; code: string; line: number }> {
    const blocks: Array<{ language: string; code: string; line: number }> = [];
    const lines = content.split('\n');
    
    let inCodeBlock = false;
    let currentBlock = { language: '', code: '', line: 0 };
    
    lines.forEach((line, index) => {
      if (line.startsWith('```')) {
        if (inCodeBlock) {
          // End of code block
          blocks.push(currentBlock);
          inCodeBlock = false;
        } else {
          // Start of code block
          currentBlock = {
            language: line.substring(3).trim(),
            code: '',
            line: index + 1
          };
          inCodeBlock = true;
        }
      } else if (inCodeBlock) {
        currentBlock.code += line + '\n';
      }
    });
    
    return blocks;
  }

  /**
   * Extract links from markdown content
   */
  private extractLinks(content: string): string[] {
    const linkRegex = /\[([^\]]+)\]\(([^)]+)\)/g;
    const links: string[] = [];
    let match;
    
    while ((match = linkRegex.exec(content)) !== null) {
      if (match[2]) {
        links.push(match[2]);
      }
    }
    
    return links;
  }
}

async function main() {
  // Check for --coverage-only flag
  const coverageOnly = process.argv.includes('--coverage-only');
  
  const config: ValidationConfig = {
    requireJSDoc: true,
    requireAPIDocumentation: !coverageOnly,
    requireModuleREADMEs: !coverageOnly,
    validateExamples: !coverageOnly,
    checkBrokenLinks: !coverageOnly,
    excludePatterns: [
      '**/*.d.ts',
      '**/generated/**',
      '**/build/**'
    ]
  };

  const validator = new DocumentationValidator(config);
  const result = await validator.validate();

  // Exit with error code if validation failed
  process.exit(result.passed ? 0 : 1);
}

// =============================================================================
// MAIN EXECUTION
// =============================================================================

main()
  .then(() => {
    console.log('\n✅ Documentation validation complete.');
  })
  .catch((error: Error) => {
    console.error('\n❌ An unexpected error occurred during documentation validation:');
    console.error(error);
    process.exit(1);
  });

export type { ValidationConfig, ValidationResult };
export { DocumentationValidator }; 