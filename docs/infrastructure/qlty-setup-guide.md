# 📊 TRAIDER V1 - Qlty CLI Setup & Integration Guide

## Overview

This guide covers the complete setup and integration of Qlty CLI (CodeClimate's command-line tool) for institutional-grade code quality analysis in TRAIDER V1. Qlty replaces the previous CodeClimate SaaS integration with a local CLI-based approach for better security and control.

## 🎯 Why Qlty CLI?

### Benefits for Trading Systems
- **Data Residency**: All analysis runs locally - no code sent to external services
- **Security**: Fits least-privilege principle for institutional environments
- **Deterministic**: Consistent results across environments
- **Integration**: Native SARIF output for GitHub Security tab
- **Performance**: Faster execution than SaaS alternatives

### Quality Standards
- **Complexity Threshold**: ≤12 (optimized for trading logic)
- **Duplication Limit**: ≤3% (zero tolerance for critical paths)
- **Maintainability**: ≥80 score (institutional grade)
- **Coverage Integration**: Works with existing coverage reports

## 🚀 Quick Start

### 1. Automated Setup (Windows)
```powershell
# Run automated setup script
npm run setup:qlty

# Or manually with parameters
.\scripts\setup-qlty.ps1 -Force
```

### 2. Manual Setup (Linux/macOS)
```bash
# Download and install Qlty CLI
curl -sSL https://github.com/qltysh/qlty/releases/latest/download/qlty-linux-x86_64.tar.gz | tar -xz
sudo mv qlty /usr/local/bin/qlty
chmod +x /usr/local/bin/qlty

# Verify installation
qlty --version

# Initialize configuration
qlty init --config .qlty.toml
```

### 3. Verify Setup
```bash
# Test configuration
qlty check --dry-run

# Run analysis
npm run quality:qlty

# View results
ls -la quality-reports/qlty/
```

## 📋 Configuration

### Primary Configuration: `.qlty.toml`

```toml
[workspace]
name = "traider-v1"
description = "Institutional-Grade Autonomous Crypto Trading Platform"

[quality]
# Institutional standards for trading systems
complexity_threshold = 12      # Sophisticated trading logic allowed
duplication_threshold = 3      # Minimum duplicated blocks
maintainability_threshold = 4.0  # Institutional target

# Coverage requirements (integrated with existing system)
coverage_threshold = 80.0      # Global minimum
trading_coverage_threshold = 90.0  # Trading logic
risk_coverage_threshold = 100.0    # Risk management

[languages.typescript]
enabled = true
extensions = [".ts", ".tsx"]
plugins = ["eslint", "tsc"]

[plugins.eslint]
enabled = true
config_file = ".eslintrc.json"
security_config = ".eslintrc.security.js"

# Trading-specific rules
[rules.risk_management]
enabled = true
patterns = ["app/risk/**", "backend/services/risk*"]
complexity_limit = 8
coverage_requirement = 100.0

[rules.trading_logic]
enabled = true
patterns = ["app/signals/**", "backend/services/trading*"]
complexity_limit = 12
coverage_requirement = 90.0

[reporting]
formats = ["json", "sarif", "junit"]
output_dir = "quality-reports/qlty"
github_annotations = true
```

### Environment Variables

Add to your `.env` file:
```bash
# Qlty configuration
QLTY_CONFIG_FILE=.qlty.toml
QLTY_OUTPUT_DIR=quality-reports/qlty
QLTY_PARALLEL_JOBS=4
QLTY_TIMEOUT=180
QLTY_FAIL_ON_ERROR=true
QLTY_GITHUB_ANNOTATIONS=true
```

## 🔧 Local Development Usage

### Basic Commands
```bash
# Run full quality analysis
npm run quality:qlty

# Initialize/reinitialize configuration
npm run quality:qlty:init

# Auto-format fixable issues
npm run quality:qlty:format

# Direct CLI usage
qlty check                    # Full analysis
qlty check --dry-run         # Validate configuration
qlty check --help            # Show all options
```

### Advanced Usage
```bash
# Analyze specific directories
qlty check app/lib/trading/ app/signals/

# Custom output formats
qlty check --format json --format sarif

# Parallel execution
qlty check --parallel-jobs 8

# Timeout control
qlty check --timeout 300
```

### Integration with Existing Workflow
```bash
# Combined quality analysis
npm run quality:all

# This runs:
# 1. Complexity analysis
# 2. Duplication detection  
# 3. Qlty quality analysis
# 4. Coverage enforcement
```

## 🚀 CI/CD Integration

### GitHub Actions Integration

The Qlty analysis is integrated into the existing code quality pipeline:

```yaml
# .github/workflows/code-quality.yml
qlty-analysis:
  name: 📈 Qlty Code Quality Analysis
  runs-on: ubuntu-latest
  needs: coverage-analysis
  timeout-minutes: 15
  
  steps:
    - name: 🔧 Install Qlty CLI
      run: |
        curl -sSL https://github.com/qltysh/qlty/releases/latest/download/qlty-linux-x86_64.tar.gz | tar -xz
        sudo mv qlty /usr/local/bin/qlty
        qlty --version
    
    - name: 📊 Run Qlty analysis
      run: |
        qlty check \
          --config .qlty.toml \
          --output-dir quality-reports/qlty \
          --format json --format sarif --format junit \
          --parallel-jobs 4 --timeout 180 \
          app/ middleware.ts shared/
    
    - name: 📊 Upload SARIF to GitHub Security
      uses: github/codeql-action/upload-sarif@v3
      with:
        sarif_file: quality-reports/qlty/results.sarif
```

### Pipeline Integration Points

1. **Phase 3**: Qlty analysis runs after coverage analysis
2. **Quality Gate**: Results feed into deployment decisions
3. **Security Tab**: SARIF results appear in GitHub Security
4. **Artifacts**: Reports stored for 90 days
5. **Notifications**: Integrated with existing alert system

## 📊 Output & Reporting

### Report Formats

1. **JSON**: Machine-readable results for automation
2. **SARIF**: GitHub Security tab integration
3. **JUnit**: Test result format for CI systems
4. **Console**: Human-readable terminal output

### Report Structure
```
quality-reports/qlty/
├── results.json       # Detailed analysis results
├── results.sarif      # GitHub Security integration
├── results.junit.xml  # CI/CD integration
└── summary.txt        # Human-readable summary
```

### Key Metrics Tracked

| Metric | Threshold | Critical Path |
|--------|-----------|---------------|
| **Quality Score** | ≥80 | All components |
| **Complexity** | ≤12 | Trading logic |
| **Duplication** | ≤3% | Risk management |
| **Maintainability** | A rating | All code |
| **Technical Debt** | ≤24 hours | Critical issues |

## 🛡️ Security Integration

### SARIF Upload
Qlty results automatically upload to GitHub Security tab:
- **Code scanning alerts**: Quality issues as security findings
- **Trend analysis**: Track quality over time
- **Pull request integration**: Inline comments on changes

### Security-Focused Rules
```toml
[security]
enabled = true
patterns = [
    "hardcoded_secrets",
    "sql_injection", 
    "xss_vulnerabilities",
    "authentication_bypass"
]
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Installation Problems
```powershell
# Windows: PowerShell execution policy
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Linux: Permission issues  
sudo chmod +x /usr/local/bin/qlty
```

#### 2. Configuration Errors
```bash
# Validate configuration
qlty check --dry-run

# Common fixes
qlty init --config .qlty.toml --force
```

#### 3. Performance Issues
```bash
# Reduce parallel jobs
qlty check --parallel-jobs 2

# Increase timeout
qlty check --timeout 300

# Exclude large directories
# Add to .qlty.toml [ignore] patterns
```

#### 4. CI/CD Integration
```yaml
# Ensure proper artifact upload
- name: 📤 Upload Qlty reports
  uses: actions/upload-artifact@v4
  if: always()  # Upload even on failure
  with:
    name: qlty-reports
    path: quality-reports/qlty/
```

### Debug Mode
```bash
# Enable verbose logging
QLTY_LOG_LEVEL=debug qlty check

# Check configuration parsing
qlty config validate

# Test specific rules
qlty check --rules complexity,duplication
```

## 📈 Quality Metrics Dashboard

### Local Monitoring
```bash
# Generate quality summary
npm run quality:all

# View detailed reports
open quality-reports/qlty/results.json

# Track trends over time
git log --oneline | head -10 | while read commit; do
  git checkout $commit
  qlty check --format json > "quality-$commit.json"
done
```

### Integration with Existing Tools

1. **SonarQube**: Complementary analysis (self-hosted)
2. **Coverage Reports**: Uses existing Vitest coverage
3. **Security Scanning**: Works with Semgrep, CodeQL
4. **Renovate**: Quality checks on dependency updates

## 🚀 Best Practices

### Development Workflow
1. **Pre-commit**: Run `npm run quality:qlty` before commits
2. **Pull Requests**: Automated analysis in CI/CD
3. **Regular Reviews**: Weekly quality metric reviews
4. **Trend Analysis**: Monitor quality score over time

### Configuration Management
1. **Version Control**: Always commit `.qlty.toml` changes
2. **Environment Consistency**: Same config across dev/CI
3. **Rule Updates**: Document rule changes in ADRs
4. **Threshold Tuning**: Adjust based on team feedback

### Performance Optimization
1. **Parallel Execution**: Use `--parallel-jobs` appropriately
2. **Selective Analysis**: Target specific directories when needed
3. **Caching**: Leverage CI cache for repeated runs
4. **Incremental**: Focus on changed files in PRs

## 📚 Additional Resources

- **Qlty Documentation**: https://github.com/qltysh/qlty
- **SARIF Specification**: https://sarifweb.azurewebsites.net/
- **TRAIDER Quality Standards**: `docs/infrastructure/code-quality-pipeline.md`
- **Setup Script**: `scripts/setup-qlty.ps1`
- **Configuration**: `.qlty.toml`

---

*This guide is part of TRAIDER V1's institutional-grade development infrastructure. For questions or improvements, please create an issue or ADR.* 