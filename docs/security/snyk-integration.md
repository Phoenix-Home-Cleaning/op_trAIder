# 🛡️ Snyk Security Integration Guide

## Overview

This document describes the comprehensive Snyk security integration for TRAIDER V1, providing institutional-grade vulnerability scanning and security monitoring for our autonomous trading platform.

## 🎯 Integration Scope

### Scan Types Implemented

1. **Open Source Dependencies** 📦
   - npm packages (frontend)
   - pip packages (backend)
   - Automated vulnerability detection
   - License compliance checking

2. **Container Security** 🐳
   - Docker image vulnerability scanning
   - Base image security analysis
   - Runtime security recommendations

3. **Infrastructure as Code** 🏗️
   - Kubernetes manifests
   - Docker Compose files
   - Security misconfigurations

## 🔧 Setup & Configuration

### Prerequisites

1. **Snyk Account**: Create account at [snyk.io](https://snyk.io)
2. **API Token**: Generate from Account Settings → API Token
3. **GitHub Secrets**: Configure `SNYK_TOKEN` in repository secrets

### Token Setup

```bash
# Local development
export SNYK_TOKEN="your-40-character-token"

# Or store in .env.local
echo "SNYK_TOKEN=your-40-character-token" >> .env.local
```

### CLI Installation

```bash
# Global installation
npm install -g snyk

# Verify installation
snyk --version

# Authenticate
snyk auth
```

## 🚀 Usage

### Local Development

```bash
# Quick vulnerability scan
npm run security:snyk

# Monitor project (sends results to Snyk dashboard)
npm run security:snyk:monitor

# Container scanning
npm run security:snyk:container

# Infrastructure as Code scanning
npm run security:snyk:iac

# Interactive fix wizard
npm run security:snyk:fix
```

### Advanced CLI Usage

```bash
# Test with specific severity threshold
snyk test --severity-threshold=high

# Generate JSON report
snyk test --json > snyk-report.json

# Test specific file
snyk test --file=package.json

# Container scan with detailed output
snyk container test traider-frontend:latest --json

# IaC scan with custom policies
snyk iac test infrastructure/ --policy-path=.snyk
```

## 🔄 CI/CD Integration

### Automated Workflows

The project includes two Snyk-enabled workflows:

1. **Security Workflow** (`.github/workflows/security.yml`)
   - Integrated Snyk scanning alongside other security tools
   - Runs on every PR and push to main/develop

2. **Dedicated Snyk Workflow** (`.github/workflows/snyk-security.yml`)
   - Comprehensive Snyk-only scanning
   - Parallel execution across scan types
   - Advanced reporting and monitoring

### Workflow Triggers

```yaml
# Automatic triggers
on:
  push:
    branches: [main, develop]
    paths:
      - 'package*.json'
      - 'requirements*.txt'
      - 'Dockerfile*'
      - 'infrastructure/**'

  pull_request:
    branches: [main, develop]

  schedule:
    - cron: '0 1 * * *' # Daily at 1 AM UTC
```

### Manual Execution

```bash
# Trigger via GitHub CLI
gh workflow run "Snyk Security Scanning" \
  --field scan_type=all \
  --field severity_threshold=medium \
  --field monitor_only=false
```

## 📊 Quality Gates & Thresholds

### Vulnerability Limits

```yaml
# Production thresholds
CRITICAL_VULN_LIMIT: 0 # Zero tolerance for critical
HIGH_VULN_LIMIT: 5 # Maximum 5 high severity
MEDIUM_VULN_LIMIT: 20 # Maximum 20 medium severity

# Container-specific (more strict)
CONTAINER_CRITICAL_LIMIT: 0
CONTAINER_HIGH_LIMIT: 2

# IaC-specific
IAC_CRITICAL_LIMIT: 0
IAC_HIGH_LIMIT: 3
```

### Deployment Blocking

- **Critical vulnerabilities**: Always block deployment
- **High vulnerabilities**: Block if exceeding limits
- **Medium vulnerabilities**: Warning only (configurable)
- **Container issues**: Stricter thresholds due to runtime exposure

## 📈 Monitoring & Reporting

### Snyk Dashboard

All scans automatically report to the Snyk dashboard:

- Project overview and health scores
- Vulnerability trends over time
- Dependency update recommendations
- License compliance status

### GitHub Security Tab

Results are uploaded as SARIF files to GitHub's Security tab:

- Code scanning alerts
- Dependency alerts
- Security advisories integration

### Workflow Summaries

Each scan generates detailed markdown summaries:

```markdown
## 📦 npm Dependencies - Snyk Scan Results

| Severity  | Count  |
| --------- | ------ |
| Critical  | 0      |
| High      | 2      |
| Medium    | 5      |
| Low       | 12     |
| **Total** | **19** |

### 🔧 Remediation Advice

- Run `npm audit fix` to automatically fix vulnerabilities
- Use `snyk wizard` for guided remediation
- Consider `npm update` for patch updates
```

## 🔧 Configuration Files

### `.snyk` Policy File

Create `.snyk` in project root for custom policies:

```yaml
# Snyk (https://snyk.io) policy file
version: v1.25.0

# Ignore specific vulnerabilities (with justification)
ignore:
  'SNYK-JS-LODASH-567746':
    - '*':
        reason: 'False positive - not exploitable in our context'
        expires: '2024-12-31T23:59:59.999Z'

# Patch rules
patch: {}

# Language settings
language-settings:
  javascript:
    packageManager: npm
  python:
    packageManager: pip
```

### Package.json Integration

```json
{
  "scripts": {
    "security:snyk": "snyk test --all-projects --severity-threshold=medium",
    "security:snyk:monitor": "snyk monitor --all-projects",
    "security:snyk:container": "snyk container test traider-frontend:latest --severity-threshold=high",
    "security:snyk:iac": "snyk iac test infrastructure/ --severity-threshold=medium",
    "security:snyk:fix": "snyk wizard"
  }
}
```

## 🚨 Incident Response

### Critical Vulnerability Detected

1. **Immediate Actions**:

   ```bash
   # Stop all deployments
   gh workflow disable "Deploy to Production"

   # Generate detailed report
   snyk test --json > critical-vuln-report.json

   # Check for available fixes
   snyk wizard
   ```

2. **Assessment Process**:
   - Evaluate vulnerability impact on trading operations
   - Check if vulnerability is exploitable in our environment
   - Determine if immediate hotfix is required

3. **Remediation Steps**:

   ```bash
   # Apply automatic fixes
   npm audit fix

   # Manual updates if needed
   npm update package-name

   # Verify fix
   snyk test --file=package.json

   # Re-enable deployments
   gh workflow enable "Deploy to Production"
   ```

### False Positive Handling

```bash
# Add to .snyk policy file
snyk ignore --id=SNYK-JS-PACKAGE-123456 \
  --reason="False positive - not exploitable" \
  --expires="2024-12-31"
```

## 🔄 Maintenance & Updates

### Token Rotation (Every 90 Days)

1. Generate new token in Snyk dashboard
2. Update `SNYK_TOKEN` in GitHub secrets
3. Test token validity:
   ```bash
   curl -H "Authorization: token NEW_TOKEN" \
        "https://api.snyk.io/v1/user/me"
   ```

### Dependency Updates

```bash
# Update Snyk CLI
npm update -g snyk

# Update Snyk GitHub Actions
# Check .github/workflows/ for latest versions
```

### Policy Reviews

- **Monthly**: Review ignored vulnerabilities
- **Quarterly**: Update severity thresholds
- **Annually**: Comprehensive policy audit

## 📚 Best Practices

### Development Workflow

1. **Pre-commit**: Run `npm run security:snyk` before committing
2. **PR Review**: Check Snyk results in workflow summaries
3. **Dependency Updates**: Use Renovate for automated updates
4. **Regular Monitoring**: Review Snyk dashboard weekly

### Security Considerations

- **Never ignore critical vulnerabilities** without security team approval
- **Document all policy exceptions** with business justification
- **Rotate tokens regularly** (90-day maximum)
- **Monitor for new vulnerabilities** in existing dependencies

### Performance Optimization

```bash
# Use --all-projects for monorepo scanning
snyk test --all-projects

# Cache results for faster subsequent runs
snyk test --cache

# Parallel scanning in CI
jobs:
  snyk-npm:
    runs-on: ubuntu-latest
  snyk-pip:
    runs-on: ubuntu-latest
```

## 🔗 Integration with Other Tools

### Renovate Integration

Renovate automatically considers Snyk vulnerability data:

```json
{
  "vulnerabilityAlerts": {
    "enabled": true,
    "schedule": ["at any time"],
    "prPriority": 10
  }
}
```

### SonarQube Integration

Snyk results can be imported into SonarQube:

```bash
# Export Snyk results
snyk test --json > snyk-results.json

# Import to SonarQube (requires plugin)
sonar-scanner -Dsonar.snyk.reportPaths=snyk-results.json
```

## 📞 Support & Troubleshooting

### Common Issues

1. **Token Authentication Failures**:

   ```bash
   # Verify token
   snyk config get api

   # Re-authenticate
   snyk auth
   ```

2. **Rate Limiting**:

   ```bash
   # Use --sequential for large projects
   snyk test --all-projects --sequential
   ```

3. **False Positives**:
   - Review vulnerability details in Snyk dashboard
   - Check if issue applies to your usage
   - Add to `.snyk` policy if confirmed false positive

### Getting Help

- **Snyk Documentation**: [docs.snyk.io](https://docs.snyk.io)
- **Community Support**: [community.snyk.io](https://community.snyk.io)
- **GitHub Issues**: Use repository issue tracker for integration problems

## 🎯 Roadmap

### Planned Enhancements

- [ ] Snyk Code (SAST) integration
- [ ] Custom security policies for trading logic
- [ ] Integration with threat intelligence feeds
- [ ] Automated vulnerability patching
- [ ] Real-time security monitoring

### Version History

- **v1.0**: Initial Snyk integration with basic scanning
- **v1.1**: Added container and IaC scanning
- **v1.2**: Enhanced CI/CD integration and reporting
- **v1.3**: Advanced policy management and monitoring

---

_This document is part of the TRAIDER V1 security framework. For questions or updates, contact the security team._
