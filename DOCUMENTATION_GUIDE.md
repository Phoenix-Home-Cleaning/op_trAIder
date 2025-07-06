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
 * @fileoverview Calculates position size based on volatility.
 * @module shared/utils/position-sizing
 *
 * @description
 * This function determines the appropriate position size for a trade
 * based on a volatility-targeting model, ensuring that the risk taken
 * is proportional to the signal strength and market conditions.
 *
 * @param {object} params - The parameters for the calculation.
 * @param {number} params.signal - Trading signal strength (-1 to 1).
 * @param {number} params.volatility - Annualized historical volatility.
 * @param {number} params.riskBudget - Available risk budget in USD.
 * @returns {number} Position size in USD, clamped to risk limits.
 *
 * @example
 * const size = calculatePositionSize({ signal: 0.5, volatility: 0.2, riskBudget: 10000 });
 * console.log(size); // 25000
 */
function calculatePositionSize(params: {
  signal: number;
  volatility: number;
  riskBudget: number;
}): number {
  // Implementation
}
```

### 2. Architecture Diagrams
**Generated from**: Code structure analysis and manual Mermaid definitions.
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
 * @api {get} /api/positions Retrieve trading positions
 * @apiName GetPositions
 * @apiGroup Trading
 * @apiVersion 1.0.0
 *
 * @apiParam {String} [symbol] Optional symbol filter (e.g., BTC-USD).
 * @apiParam {String} [timeRange] Time range for position history (e.g., '1D', '7D').
 *
 * @apiSuccess {Object[]} positions List of position objects.
 * @apiSuccess {String} positions.symbol The asset symbol.
 * @apiSuccess {Number} positions.size The size of the position.
 * @apiSuccess {Number} positions.entryPrice The average entry price.
 * @apiSuccess {Number} positions.pnl The unrealized profit and loss.
 *
 * @apiSuccessExample {json} Success-Response:
 *     HTTP/1.1 200 OK
 *     [
 *       {
 *         "symbol": "BTC-USD",
 *         "size": 1.5,
 *         "entryPrice": 60000,
 *         "pnl": 7500
 *       }
 *     ]
 *
 * @apiError (401 Unauthorized) {String} error The user is not authenticated.
 * @apiError (500 InternalServerError) {String} error An issue occurred on the server.
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
npx tsx scripts/create-adr.ts "Migrate to GraphQL API"

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
 * // Expected output: { value: 'processed:input' }
 * ```
 * 
 * @see {@link RelatedFunction} for related functionality
 * @since 1.0.0
 */
function myFunction(paramName: string, optionalParam?: number): { value: string } {
  // Implementation
  return { value: `processed:${paramName}` };
}
```

### ADR Writing Guidelines

1. **Context**: Clearly explain the problem or decision needed.
2. **Decision**: Document the chosen solution and provide justification. List alternatives considered and why they were not chosen.
3. **Consequences**: List both positive and negative outcomes of the decision.
4. **Implementation Plan**: Provide actionable steps, success criteria, and a timeline.
5. **Monitoring & Review**: Define metrics to track success and a schedule for reviewing the decision.

### API Documentation Guidelines

Use a combination of file-level documentation and OpenAPI-style annotations within your route handlers to ensure that API documentation is thorough and auto-generatable.

```typescript
/**
 * @fileoverview Endpoint for managing user trade settings.
 * @module app/api/settings/trading/route
 */

import { NextResponse } from 'next/server';

/**
 * @api {post} /api/settings/trading Update user trading settings
 * @apiName UpdateTradeSettings
 * @apiGroup Settings
 * @apiVersion 1.0.0
 *
 * @apiBody {Object} settings The new trading settings.
 * @apiBody {String} settings.defaultOrderType The default order type ('MARKET' or 'LIMIT').
 * @apiBody {Number} settings.maxSlippageBps The maximum slippage in basis points.
 *
 * @apiSuccess (200) {Object} data Confirmation message.
 * @apiSuccess (200) {String} data.message Success message.
 *
 * @apiError (400) {String} error Invalid settings provided.
 */
export async function POST(request: Request) {
  const settings = await request.json();
  // ... validation and update logic
  return NextResponse.json({ message: 'Settings updated successfully' });
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

## 📋 Environment Configuration

### Unified Environment Management

As of ADR-006 (2025-01-27), all environment variables are managed through a single root-level configuration:

- **`.env`**: All environment variables (frontend + backend, gitignored)
- **`.env.example`**: Complete template with all required variables
- **Location**: Project root directory (not in `/backend`)

### Setup Process
```bash
# Copy template to create environment file
cp .env.example .env

# Edit with your configuration
nano .env

# Generate secure secrets (optional)
.\scripts\generate-secrets.ps1
```

### Security Requirements
- All sensitive variables must be set via environment (never hardcoded)
- Use cryptographically secure secrets (256-bit minimum)
- Proper file permissions: `chmod 600 .env`
- Never commit actual secrets to version control

## 📝 Documentation Standards

> **Note**: This documentation automation system is designed to grow with TRAIDER V1 from MVP through institutional-grade deployment. The system automatically adapts to codebase changes while maintaining professional documentation standards required for institutional cryptocurrency trading platforms. 