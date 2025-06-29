# 📚 TRAIDER Documentation Automation Guide

*Complete guide to using the automated documentation system for TRAIDER V1*

---

## 🎯 Overview

TRAIDER's documentation automation system ensures that documentation stays synchronized with code through automated generation, validation, and deployment. This system is designed for institutional-grade software development with comprehensive coverage and professional presentation.

---

## 🚀 Quick Start

### Generate Documentation
```bash
# Generate all documentation
npm run docs:generate

# Generate only API documentation
npm run docs:api

# Build complete documentation suite
npm run docs:build
```

### Validate Documentation
```bash
# Validate documentation completeness
npm run docs:validate

# Check coverage only
npm run docs:coverage

# Watch for changes and regenerate
npm run docs:watch
```

### Create Architecture Decision Record
```bash
# Create new ADR
npm run adr:new "Use GraphQL for API Layer"

# List existing ADRs
npm run adr:list
```

---

## 📖 Documentation Types

### 1. API Documentation (TypeDoc)
**Generated from**: JSDoc comments in TypeScript files  
**Output**: `docs/api/`  
**Format**: Markdown with HTML navigation

**Example JSDoc Comment**:
```typescript
/**
 * Calculates position size based on volatility targeting
 * 
 * @param signal - Trading signal strength (-1 to 1)
 * @param volatility - Historical volatility (annualized)
 * @param riskBudget - Available risk budget in USD
 * @returns Position size in USD, clamped to risk limits
 * 
 * @example
 * ```typescript
 * const size = calculatePositionSize(0.5, 0.2, 10000);
 * console.log(size); // 2500
 * ```
 */
function calculatePositionSize(
  signal: number,
  volatility: number,
  riskBudget: number
): number {
  // Implementation
}
```

### 2. Architecture Diagrams
**Generated from**: Code structure analysis  
**Output**: `docs/diagrams/`  
**Format**: Mermaid diagrams

**Auto-generated diagrams**:
- System overview
- Component interactions
- Data flow
- Dependency graphs

### 3. OpenAPI Specification
**Generated from**: Next.js API route handlers  
**Output**: `docs/api/openapi.json` and `docs/api/openapi.yaml`  
**Format**: OpenAPI 3.0

**Example API Route Documentation**:
```typescript
/**
 * @fileoverview Portfolio positions API endpoint
 * 
 * Retrieves current trading positions with real-time P&L calculations.
 * Supports filtering by symbol and time range.
 */

/**
 * GET /api/positions - Retrieve trading positions
 * 
 * @param symbol - Optional symbol filter (e.g., BTC-USD)
 * @param timeRange - Time range for position history
 * @returns Array of position objects with P&L data
 */
export async function GET(request: Request) {
  // Implementation
}
```

### 4. Architecture Decision Records (ADRs)
**Created manually**: Using ADR template and tooling  
**Output**: `docs/adr/`  
**Format**: Structured markdown documents

**Usage**:
```bash
# Create new ADR
npm run adr:new "Migrate to GraphQL API"

# This creates: docs/adr/adr-002-migrate-to-graphql-api.md
# Opens in VS Code for editing
```

### 5. Performance Documentation
**Generated from**: Benchmark test results  
**Output**: `docs/performance/`  
**Format**: Markdown with metrics and charts

### 6. Runbooks
**Generated from**: Code comments and templates  
**Output**: `docs/runbooks/`  
**Format**: Operational procedures and troubleshooting guides

---

## 🔍 Documentation Validation

### Validation Rules

1. **JSDoc Coverage**: All public functions must have JSDoc comments
2. **API Documentation**: All API routes must have endpoint documentation
3. **Module READMEs**: Each major directory should have a README.md
4. **Example Compilation**: Code examples must compile successfully
5. **Link Validity**: Internal links must point to existing files

### Validation Levels

#### ✅ Passing Criteria
- JSDoc coverage ≥ 90%
- All API routes documented
- No broken internal links
- All code examples compile

#### ⚠️ Warning Criteria
- JSDoc coverage 85-89%
- Missing module READMEs
- Potentially broken external links

#### ❌ Failing Criteria
- JSDoc coverage < 85%
- Undocumented API routes
- Broken internal links
- Code examples that don't compile

---

## 🛠️ CI/CD Integration

### GitHub Actions Workflow

The documentation system runs automatically on:
- **Push to main**: Full documentation generation and deployment
- **Pull requests**: Validation and coverage reporting
- **Daily schedule**: Documentation drift detection

### Workflow Jobs

1. **validate-docs**: Validates documentation completeness
2. **generate-docs**: Generates all documentation artifacts
3. **check-coverage**: Reports documentation coverage
4. **performance-docs**: Generates performance documentation
5. **notify-completion**: Sends completion notifications

### Artifacts

- **Documentation site**: Deployed to GitHub Pages
- **Coverage reports**: Available for 30 days
- **Performance reports**: Available for 30 days
- **Generated documentation**: Available for 90 days

---

## 📝 Writing Guidelines

### JSDoc Best Practices

```typescript
/**
 * @fileoverview Brief description of the file's purpose
 * 
 * Longer description explaining the file's role in the system,
 * key concepts, and how it fits into the overall architecture.
 * 
 * @author TRAIDER Team
 * @since 2025-06-29
 */

/**
 * Function description explaining what it does
 * 
 * @param paramName - Description of parameter
 * @param optionalParam - Optional parameter description
 * @returns Description of return value
 * 
 * @throws {Error} When invalid input is provided
 * 
 * @example
 * ```typescript
 * const result = myFunction('input', 42);
 * console.log(result); // Expected output
 * ```
 * 
 * @see {@link RelatedFunction} for related functionality
 * @since 1.0.0
 */
function myFunction(paramName: string, optionalParam?: number): ReturnType {
  // Implementation
}
```

### ADR Writing Guidelines

1. **Context**: Clearly explain the problem or decision needed
2. **Decision**: Document the chosen solution and alternatives considered
3. **Consequences**: List both positive and negative outcomes
4. **Implementation**: Provide actionable steps and success criteria
5. **Monitoring**: Define metrics and review schedule

### API Documentation Guidelines

```typescript
/**
 * @fileoverview API endpoint description
 * 
 * Detailed explanation of the endpoint's purpose, authentication
 * requirements, rate limits, and usage patterns.
 */

/**
 * HTTP_METHOD /api/endpoint - Brief endpoint description
 * 
 * Detailed description of what the endpoint does, including:
 * - Authentication requirements
 * - Request/response formats
 * - Error conditions
 * - Rate limiting
 * 
 * @param param1 - Request parameter description
 * @param param2 - Optional parameter description
 * @returns Response object description
 * 
 * @throws {400} Bad Request - Invalid parameters
 * @throws {401} Unauthorized - Missing or invalid authentication
 * @throws {429} Too Many Requests - Rate limit exceeded
 * 
 * @example
 * ```typescript
 * const response = await fetch('/api/endpoint', {
 *   method: 'POST',
 *   headers: { 'Content-Type': 'application/json' },
 *   body: JSON.stringify({ param1: 'value' })
 * });
 * ```
 */
export async function POST(request: Request) {
  // Implementation
}
```

---

## 🔧 Configuration

### TypeDoc Configuration (`typedoc.json`)
```json
{
  "entryPoints": ["app/lib", "app/hooks", "app/components"],
  "out": "docs/api",
  "plugin": ["typedoc-plugin-markdown", "typedoc-plugin-mermaid"],
  "includeVersion": true,
  "excludePrivate": false,
  "categorizeByGroup": true
}
```

### Documentation Generation Config
```typescript
const config: DocumentationConfig = {
  outputDir: 'docs',
  sourceDir: 'app',
  includePrivate: false,
  generateDiagrams: true,
  generateOpenAPI: true,
  generateMetrics: true
};
```

### Validation Config
```typescript
const config: ValidationConfig = {
  requireJSDoc: true,
  requireAPIDocumentation: true,
  requireModuleREADMEs: true,
  validateExamples: true,
  checkBrokenLinks: true
};
```

---

## 📊 Monitoring & Metrics

### Documentation Health Metrics

- **Coverage Percentage**: JSDoc coverage across codebase
- **Validation Success Rate**: Percentage of successful validation runs
- **Build Success Rate**: Documentation generation success rate
- **Link Health**: Percentage of valid internal links
- **Example Accuracy**: Percentage of compilable code examples

### Performance Metrics

- **Generation Time**: Time to generate complete documentation
- **Validation Time**: Time to validate documentation completeness
- **Build Pipeline Impact**: Additional CI/CD time for documentation
- **Storage Usage**: Documentation artifact storage requirements

---

## 🚨 Troubleshooting

### Common Issues

#### Documentation Generation Fails
```bash
# Check TypeDoc installation
npm list typedoc

# Reinstall dependencies
npm ci

# Run with verbose output
npx typedoc --help
```

#### Validation Errors
```bash
# Check specific validation issues
npm run docs:validate -- --verbose

# Generate coverage report
npm run docs:coverage

# Fix JSDoc issues
npm run docs:validate -- --fix-jsdoc
```

#### Missing Dependencies
```bash
# Install required packages
npm install -D typedoc typedoc-plugin-markdown typedoc-plugin-mermaid

# Install global tools
npm install -g tsx
```

#### CI/CD Issues
- Check GitHub Actions logs for specific errors
- Verify required secrets are configured
- Ensure proper permissions for GitHub Pages deployment

---

## 🎯 Success Criteria

### Documentation Quality
- ✅ 100% of public APIs documented with JSDoc
- ✅ All API endpoints have OpenAPI specifications
- ✅ Architecture decisions tracked in ADRs
- ✅ Code examples compile and run correctly
- ✅ Internal links are valid and up-to-date

### Automation Effectiveness
- ✅ Documentation updates automatically on code changes
- ✅ Validation prevents incomplete documentation from merging
- ✅ New developers can onboard using only documentation
- ✅ Documentation site is professionally presented
- ✅ Performance benchmarks are automatically updated

### Institutional Standards
- ✅ Complete audit trail of architectural decisions
- ✅ Professional documentation suitable for compliance review
- ✅ Comprehensive operational runbooks for production systems
- ✅ Performance documentation meets institutional requirements
- ✅ Documentation system scales with codebase growth

---

> **Note**: This documentation automation system is designed to grow with TRAIDER V1 from MVP through institutional-grade deployment. The system automatically adapts to codebase changes while maintaining professional documentation standards required for institutional cryptocurrency trading platforms. 