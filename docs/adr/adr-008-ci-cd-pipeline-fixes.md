# ADR-008: CI/CD Pipeline Fixes - ESLint and Vitest Configuration

## Status
**ACCEPTED** - 2025-06-30

## Context

The CI/CD pipeline encountered two critical issues that were blocking successful test execution and code quality validation:

1. **ESLint Compact Formatter Issue**: The GitHub Actions workflow was using `--format compact` flag, but the compact formatter is no longer included in ESLint core as of ESLint 9.x
2. **Vitest ES Module Compatibility Issue**: The Vitest configuration was encountering `ERR_REQUIRE_ESM` errors due to improper ES Module handling

### Technical Details

**ESLint Issue:**
- Error: `The compact formatter is no longer part of core ESLint. Install it manually with npm install -D eslint-formatter-compact`
- Location: `.github/workflows/ci.yml` line 96
- Impact: Blocked linting validation in CI/CD pipeline

**Vitest Issue:**
- Error: `Error [ERR_REQUIRE_ESM]: require() of ES Module /home/runner/work/op_trAIder/op_trAIder/node_modules/vite/dist/node/index.js`
- Location: `vitest.config.ts` configuration
- Impact: Blocked all unit and integration test execution

## Decision

### ESLint Fix
Remove the `--format compact` flag from the ESLint command in CI/CD workflow:
```yaml
# Before
npx next lint --max-warnings 0 --format compact

# After  
npx next lint --max-warnings 0
```

**Rationale:**
- The default formatter provides sufficient output for CI/CD
- Avoids adding unnecessary dependencies
- Maintains zero-warnings policy for institutional standards

### Vitest Fix
Enhanced the Vitest configuration with proper ES Module support:
```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';
import { fileURLToPath } from 'url';
import tsconfigPaths from 'vite-tsconfig-paths';

// ES Module compatibility
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
```

**Rationale:**
- Provides proper ES Module compatibility
- Maintains Node.js compatibility across different environments
- Follows modern JavaScript module standards

## Consequences

### Positive
- **Pipeline Reliability**: CI/CD pipeline now executes successfully
- **Test Coverage**: All 167 tests pass with proper coverage reporting
- **Code Quality**: ESLint validation works without external dependencies
- **Institutional Compliance**: Maintains zero-warnings policy and comprehensive testing

### Negative
- **Minor Output Change**: ESLint output format slightly different (acceptable)
- **Configuration Complexity**: Vitest config slightly more complex but more robust

## Implementation

### Files Modified
1. `.github/workflows/ci.yml` - Removed `--format compact` flag
2. `vitest.config.ts` - Added ES Module compatibility imports

### Verification
- ✅ ESLint: `npx next lint --max-warnings 0` - No warnings or errors
- ✅ Vitest: `npm run test:run` - 167 tests passing
- ✅ CI/CD: Pipeline executes without formatter or module errors

## Monitoring

### Success Metrics
- CI/CD pipeline success rate: Target 100%
- Test execution time: <30 seconds for full suite
- Zero ESLint warnings maintained

### Alerts
- Pipeline failures will trigger immediate investigation
- Test coverage drops below 95% will require review
- ESLint warnings will block deployments

## References

- [ESLint 9.x Migration Guide](https://eslint.org/docs/latest/use/migrate-to-9.0.0)
- [Vitest ES Module Configuration](https://vitest.dev/guide/migration.html)
- [TRAIDER CI/CD Pipeline Documentation](../infrastructure/ci-cd-pipeline.md)

## Review

- **Author**: TRAIDER Team
- **Reviewers**: DevOps Team, QA Team
- **Risk Assessment**: LOW - Configuration fixes with no functional impact
- **Rollback Plan**: Revert commits if any issues arise 