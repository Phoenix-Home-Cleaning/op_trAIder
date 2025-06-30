# 🤝 Contributing to TRAIDER V1

**Institutional-Grade Development Standards for Autonomous Trading Platform**

---

## 🚀 Quick Start

Welcome to TRAIDER V1! This guide covers our comprehensive pre-commit hooks and development workflow designed to maintain institutional-grade code quality.

### Prerequisites
- Node.js ≥18.0.0
- Git with Husky hooks enabled
- Understanding of conventional commits

---

## 🔒 Pre-commit Quality Gates

TRAIDER V1 implements multi-layered pre-commit validation to ensure only high-quality, secure code enters the repository.

### 🛡️ Security Checks (CRITICAL)

**Secret Detection**: Scans for hardcoded API keys, passwords, and tokens
```bash
# ❌ These will be blocked:
const API_KEY = "sk_live_DOCS_EXAMPLE"
const password = "docs_example_123"
const coinbase_secret = "docs_example_abc"

# ✅ Use environment variables instead:
const API_KEY = process.env.COINBASE_API_KEY
const password = process.env.DB_PASSWORD
```

**Large File Prevention**: Blocks files >1MB (use MLflow for models)
```bash
# ❌ Blocked: model.pkl (5.2MB)
# ✅ Use: MLflow model registry
```

### 📝 Code Quality Checks

**File Headers**: All TypeScript files must include documentation headers
```typescript
/**
 * @fileoverview Brief description of the file's purpose
 * @module path/to/module
 * 
 * @description
 * Detailed description including trading context and performance considerations
 * 
 * @author TRAIDER Team
 * @since 1.0.0-alpha
 */
```

**Error Handling**: Trading-critical files must implement proper error handling
```typescript
// ❌ Will be flagged:
async function executeTrade(): Promise<any> {
  const result = await fetch('/api/trade');
  return result.json();
}

// ✅ Proper error handling:
async function executeTrade(): Promise<any> {
  try {
    const result = await fetch('/api/trade');
    if (!result.ok) throw new Error(`Trade failed: ${result.status}`);
    return await result.json();
  } catch (error) {
    console.error('Trade execution failed', error);
    throw new Error('EXECUTION_FAILED: Retry with exponential backoff');
  }
}
```

**Timer Cleanup**: Prevent memory leaks in React components
```typescript
// ❌ Will be flagged:
useEffect(() => {
  const timer = setTimeout(() => console.log('update'), 1000);
}, []);

// ✅ Proper cleanup:
useEffect(() => {
  const timer = setTimeout(() => console.log('update'), 1000);
  return () => clearTimeout(timer);
}, []);
```

### 🧪 Testing Requirements

**No Console Statements**: Remove debug logs from production code
```typescript
// ❌ Blocked in production files:
// console.log('Debug: position size =', positionSize);

// ✅ Use proper logging:
console.debug('Position size calculated', { positionSize: 100 });
```

**No Focused Tests**: Prevent accidentally skipping tests
```typescript
// ❌ Will be blocked:
describe.only('Trading logic', () => { ... });
it.only('should calculate position size', () => { ... });

// ✅ Run all tests:
describe('Trading logic', () => { ... });
it('should calculate position size', () => { ... });
```

---

## 📋 Commit Message Format

TRAIDER V1 enforces [Conventional Commits](https://conventionalcommits.org/) for clear change tracking and automated changelog generation.

### Format
```
<type>(scope): <description>

[optional body]

[optional footer]
```

### Valid Types
- **feat**: New feature or trading strategy
- **fix**: Bug fix or trading issue resolution
- **docs**: Documentation changes
- **style**: Code formatting changes
- **refactor**: Code restructuring without behavior change
- **perf**: Performance improvements
- **test**: Test additions or modifications
- **chore**: Maintenance tasks
- **build**: Build system changes
- **ci**: CI/CD pipeline changes
- **revert**: Reverting previous commits

### Valid Scopes
- **Frontend**: `dashboard`, `charts`, `ui`, `auth`, `performance`, `risk`, `signals`, `system`
- **Backend**: `market-data`, `signal-gen`, `risk-engine`, `executor`, `portfolio`, `ml`
- **Infrastructure**: `ci`, `deployment`, `monitoring`, `security`, `database`
- **Development**: `tests`, `docs`, `scripts`, `config`, `deps`

### Examples
```bash
# ✅ Good commit messages:
feat(signals): add momentum-based trading signal with 0.65 Sharpe ratio
fix(risk): resolve position sizing calculation for volatile assets
perf(market-data): optimize WebSocket connection handling (50ms → 10ms)
docs(api): update trading endpoints with rate limiting info

# ❌ Bad commit messages:
updated stuff
fix bug
WIP
asdf
```

### Special Commit Types

**Breaking Changes**: Include `BREAKING CHANGE:` in footer
```
feat(api): restructure trading endpoints

BREAKING CHANGE: /api/trades endpoint now requires authentication header
```

**Security Commits**: Automatically flagged for review
```
fix(auth): patch JWT token validation vulnerability
```

**Performance Commits**: Require benchmark updates
```
perf(signals): optimize feature calculation pipeline
```

---

## 🔧 Development Workflow

### 1. Pre-commit Hook Execution
When you run `git commit`, the following checks execute automatically:

```bash
🚀 TRAIDER V1 Pre-commit Quality Gates
======================================
📁 Checking 5 staged files...

✅ Secret Detection: No hardcoded secrets detected
✅ File Size Check: All files within size limits
❌ File Header Check [LOW]: Found 1 file(s) missing headers
   └─ app/components/NewComponent.tsx: Missing @fileoverview in header
✅ Error Handling Check: Proper error handling detected
✅ Timer Cleanup Check: All timers have proper cleanup
✅ Console Statement Check: No console statements found
✅ Test Focus Check: No focused tests found

❌ 1 check(s) failed!
⚠️  Non-critical failures detected
💡 Consider fixing before committing
🔧 Use --no-verify to bypass (not recommended)
```

### 2. Lint-staged Integration
After custom checks pass, lint-staged runs:

```bash
🔍 Running lint-staged checks...
✔ eslint --fix --max-warnings 0
✔ prettier --write
✔ vitest run --changed --reporter=dot
```

### 3. TypeScript Compilation
```bash
📖 TypeScript files changed, checking compilation...
✔ npx tsc --noEmit --incremental false
```

### 4. Documentation Validation
```bash
📚 Validating documentation...
✔ tsx scripts/validate-docs.ts
```

### 5. Commit Message Validation
```bash
🔍 TRAIDER V1 Commit Message Validation
=======================================
✅ Commit message format validated
📝 Message: feat(signals): add momentum-based trading signal
🎯 Ready for institutional-grade commit!
```

---

## 🚨 Emergency Bypass

In critical situations, you can bypass pre-commit hooks:

```bash
# ⚠️ EMERGENCY ONLY - Use with extreme caution
git commit --no-verify -m "hotfix: emergency trading halt"

# 📋 Required follow-up actions:
# 1. Create immediate follow-up PR to fix quality issues
# 2. Document reason in commit message
# 3. Notify team of bypass usage
# 4. Schedule code review within 24 hours
```

**When to use bypass:**
- Production trading system down
- Critical security vulnerability
- Emergency market conditions

**Never bypass for:**
- "Quick fixes" during development
- Avoiding test writing
- Deadline pressure
- Code review shortcuts

---

## 📊 Performance Standards

### Pre-commit Hook Performance
- **Target runtime**: <30 seconds
- **Parallel execution**: Where possible
- **Early exit**: On critical failures
- **Resource usage**: <100MB memory

### False Positive Rates
- **Target**: <5% false positives
- **Security checks**: <1% false positives
- **Code quality**: <10% false positives

---

## 🛠️ Troubleshooting

### Common Issues

**1. "Command not found: tsx"**
```bash
npm install -g tsx
# or
npx tsx scripts/pre-commit-checks.ts
```

**2. "TypeScript compilation failed"**
```bash
# Check specific errors:
npx tsc --noEmit

# Fix import/export issues
# Ensure all types are properly defined
```

**3. "Secret detected false positive"**
```bash
# Add to .gitignore if needed:
echo "config/test-keys.json" >> .gitignore

# Or use environment variables:
const TEST_KEY = process.env.TEST_API_KEY || 'test-key-placeholder'
```

**4. "Large file blocked"**
```bash
# Move to appropriate storage:
# - Models: MLflow model registry
# - Data: Database or S3
# - Images: CDN or public folder
```

**5. "Documentation coverage insufficient"**
```bash
# Add required JSDoc headers:
npm run docs:validate
npm run docs:coverage

# Fix specific files shown in output
```

### Getting Help

1. **Check logs**: Full error details in terminal output
2. **Review examples**: See existing codebase for patterns
3. **Team consultation**: For trading-specific questions
4. **Documentation**: Refer to `docs/` folder

---

## 📈 Quality Metrics

### Code Quality Targets
- **Test coverage**: ≥90% for trading logic
- **Documentation**: 100% JSDoc coverage for public APIs
- **Linting**: Zero warnings in production code
- **Type safety**: Strict TypeScript mode

### Security Standards
- **No hardcoded secrets**: 100% compliance
- **Dependency scanning**: Weekly automated audits
- **Code scanning**: GitHub Advanced Security enabled
- **Access control**: Role-based permissions

### Performance Benchmarks
- **Build time**: <2 minutes for full build
- **Test suite**: <30 seconds for unit tests
- **Linting**: <10 seconds for changed files
- **Pre-commit**: <30 seconds total

---

## 🎯 Best Practices

### Trading Code Standards
```typescript
// ✅ Always include risk context
/**
 * Calculate position size with volatility targeting
 * 
 * @risk HIGH - Incorrect sizing can lead to significant losses
 * @tradingImpact Affects all position entries and risk management
 */
function calculatePositionSize(signal: number, volatility: number): number {
  // Implementation with proper validation
}
```

### Error Handling Patterns
```typescript
// ✅ Use typed errors with recovery strategies
class TradingError extends Error {
  constructor(
    message: string,
    public code: string,
    public severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL',
    public recovery: string
  ) {
    super(message);
  }
}

throw new TradingError(
  'Market data connection lost',
  'MARKET_DATA_DISCONNECTED',
  'CRITICAL',
  'Attempting reconnection with exponential backoff'
);
```

### Testing Requirements
```typescript
// ✅ Include performance benchmarks
describe('MarketDataService', () => {
  it('should process tick data within 1ms', async () => {
    const start = performance.now();
    await service.processTick(mockTick);
    const duration = performance.now() - start;
    expect(duration).toBeLessThan(1);
  });
});
```

---

## 📚 Additional Resources

- [TRAIDER Architecture Documentation](./docs/README.md)
- [Trading System Design Patterns](./docs/architecture/)
- [Security Guidelines](./SECURITY_SUMMARY.md)
- [Performance Benchmarking](./docs/infrastructure/)
- [API Documentation](./docs/api/)

---

**Remember**: These quality gates exist to protect our trading system and capital. Every check serves a purpose in maintaining institutional-grade reliability and security.

🎯 **Happy Trading & Contributing!**

## 📋 **Updating the CHANGELOG**

After a successful commit, if your changes are noteworthy (new features, bug fixes, performance improvements), you **must** update the `CHANGELOG.md`.

### Format
Use the following format at the top of the `CHANGELOG.md`:

```markdown
## [Version] - YYYY-MM-DD HH:MM:SS

### Trading Logic Changes
- Modified signal generation: [description]
- Risk limit adjustments: [old] → [new]

### Performance Improvements
- Reduced latency: [component] [Xms] → [Yms]

### Infrastructure
- [Changes that affect deployment/monitoring]
```

This ensures all changes are documented for audit and release purposes. 