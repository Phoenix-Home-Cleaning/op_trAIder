# 🔄 Renovate Dependency Management Guide

## Overview

This document describes the comprehensive Renovate integration for TRAIDER V1, providing institutional-grade automated dependency management for our autonomous trading platform.

## 🎯 Integration Scope

### Automated Dependency Management

1. **Open Source Dependencies** 📦
   - npm packages (frontend)
   - pip packages (backend)
   - GitHub Actions dependencies
   - Docker base images

2. **Security-First Approach** 🔒
   - Vulnerability-driven updates
   - Security advisory integration
   - Automated security patch prioritization

3. **Trading-Aware Scheduling** ⏰
   - Updates scheduled before market open
   - Stability periods for critical dependencies
   - Emergency security updates bypass scheduling

## 🔧 Setup & Configuration

### Prerequisites

1. **GitHub Account**: Repository access with appropriate permissions
2. **GitHub Token**: Fine-grained personal access token
3. **Repository Secrets**: Configure `RENOVATE_TOKEN` in GitHub secrets

### Token Setup

#### Creating a Fine-Grained Personal Access Token

1. Navigate to **GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **"Generate new token"**
3. Configure token settings:
   - **Token name**: `renovate-bot-traider`
   - **Expiration**: 90 days (for security rotation)
   - **Repository access**: Selected repositories → `your-org/traider`

4. **Required Permissions**:

   ```yaml
   Repository permissions:
     Contents: Read and write
     Pull requests: Read and write
     Issues: Read and write (optional)
     Workflows: Read and write (optional)
     Metadata: Read
   ```

5. **Store Token Securely**:
   ```bash
   # GitHub repository secrets
   RENOVATE_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx
   ```

### Local Development Setup

```bash
# Install Renovate CLI (optional)
npm install -g renovate

# Configure local environment
echo "RENOVATE_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxx" >> .env.local

# Test token validity
renovate --dry-run --autodiscover-filter=your-org/traider
```

## 📋 Configuration Overview

### Main Configuration File: `renovate.json`

The project uses a comprehensive `renovate.json` configuration with the following key features:

#### Base Configuration

```json
{
  "extends": [
    "config:base",
    "security:openssf-scorecard",
    ":dependencyDashboard",
    ":semanticCommits",
    ":separatePatchReleases",
    "group:monorepos",
    "group:recommended"
  ],
  "timezone": "Etc/UTC",
  "schedule": ["before 6am on monday"]
}
```

#### Trading-Specific Rules

```json
{
  "packageRules": [
    {
      "description": "🔒 Critical Security Updates - Immediate Priority",
      "matchPackagePatterns": ["*"],
      "vulnerabilityAlerts": {
        "enabled": true,
        "schedule": ["at any time"],
        "prPriority": 10
      }
    },
    {
      "description": "🚀 Trading Core Dependencies - High Stability Required",
      "matchPackagePatterns": ["next", "react", "typescript", "fastapi", "sqlalchemy"],
      "minimumReleaseAge": "7 days",
      "stabilityDays": 7,
      "automerge": false
    }
  ]
}
```

## 🚀 Usage

### Automated Operation

Renovate runs automatically:

- **Scheduled**: Monday-Friday at 06:00 UTC (before market open)
- **Security Updates**: Immediately when vulnerabilities are detected
- **Manual Trigger**: Via GitHub Actions workflow dispatch

### Manual Execution

```bash
# Trigger via GitHub CLI
gh workflow run "Renovate Dependency Management" \
  --field log_level=info \
  --field dry_run=false \
  --field force_refresh=true

# Local dry run
renovate --dry-run --autodiscover-filter=your-org/traider
```

### Dependency Dashboard

Renovate creates and maintains a "Dependency Dashboard" issue that provides:

- Overview of all pending updates
- Security vulnerability status
- Update scheduling information
- Manual trigger controls

## 📊 Package Rules & Prioritization

### Security Updates (Priority 10)

```json
{
  "vulnerabilityAlerts": {
    "enabled": true,
    "schedule": ["at any time"],
    "prPriority": 10,
    "labels": ["security", "critical", "immediate"]
  }
}
```

### Trading Core Dependencies (Priority 8)

```json
{
  "matchPackagePatterns": [
    "next",
    "react",
    "typescript",
    "fastapi",
    "sqlalchemy",
    "timescaledb",
    "redis",
    "kafka",
    "prometheus"
  ],
  "minimumReleaseAge": "7 days",
  "stabilityDays": 7,
  "automerge": false
}
```

### Development Dependencies (Priority 5)

```json
{
  "matchDepTypes": ["devDependencies"],
  "minimumReleaseAge": "3 days",
  "automerge": true,
  "automergeType": "pr",
  "matchUpdateTypes": ["patch", "minor"]
}
```

### Security Tools (Priority 9)

```json
{
  "matchPackagePatterns": ["trivy", "semgrep", "bandit", "safety"],
  "schedule": ["at any time"],
  "automerge": true
}
```

## 🔄 CI/CD Integration

### Workflow File: `.github/workflows/renovate.yml`

The dedicated Renovate workflow includes:

1. **Pre-flight Validation**
   - Configuration validation
   - Token permission verification
   - Execution decision logic

2. **Renovate Execution**
   - Comprehensive logging
   - Error handling and recovery
   - Post-execution security scanning

3. **Monitoring & Reporting**
   - Detailed execution summaries
   - Artifact collection
   - Failure notifications

### Workflow Triggers

```yaml
on:
  schedule:
    # Run Monday-Friday at 06:00 UTC (before market open)
    - cron: '0 6 * * 1-5'
  workflow_dispatch:
    inputs:
      log_level: # debug, info, warn, error
      dry_run: # true/false
      force_refresh: # true/false
```

### Integration with Security Scanning

After Renovate updates dependencies, automated security scans run:

```bash
# Post-Renovate security validation
npm audit --audit-level=moderate
snyk test --severity-threshold=medium
```

## 📈 Monitoring & Reporting

### GitHub Workflow Summaries

Each Renovate execution generates detailed reports:

```markdown
## 🔄 Renovate Execution Summary

| Metric           | Count |
| ---------------- | ----- |
| PRs Created      | 3     |
| PRs Updated      | 1     |
| Branches Created | 4     |
| Security Updates | 2     |
```

### Dependency Dashboard

Renovate maintains an issue with:

- All pending dependency updates
- Security vulnerability status
- Manual control options
- Update scheduling information

### Snyk Integration

Renovate considers Snyk vulnerability data:

- Prioritizes security updates
- Includes vulnerability context in PRs
- Triggers immediate updates for critical issues

## 🛡️ Security Integration

### Vulnerability-Driven Updates

```json
{
  "osvVulnerabilityAlerts": true,
  "vulnerabilityAlerts": {
    "enabled": true,
    "schedule": ["at any time"],
    "prCreation": "immediate"
  }
}
```

### Security Scanning Integration

Every Renovate PR triggers:

1. Automated security scans (Snyk, npm audit)
2. Quality gate validation
3. Performance impact assessment
4. Trading logic compatibility checks

### Emergency Security Updates

Critical security updates bypass normal scheduling:

- Immediate PR creation
- High priority labels
- Security team notification
- Expedited review process

## 🔧 Configuration Management

### Custom Managers

The configuration includes custom managers for:

1. **Docker Images in Kubernetes**:

   ```json
   {
     "customType": "regex",
     "fileMatch": ["^infrastructure/k8s/.+\\.ya?ml$"],
     "matchStrings": ["image:\\s*(?<depName>[^:]+):(?<currentValue>[^\\s]+)"],
     "datasourceTemplate": "docker"
   }
   ```

2. **Tool Versions in Scripts**:
   ```json
   {
     "customType": "regex",
     "fileMatch": ["^scripts/.+\\.sh$"],
     "matchStrings": [
       "# renovate: datasource=(?<datasource>\\S+) depName=(?<depName>\\S+)\\s+\\w+_VERSION=[\"']?(?<currentValue>[^\"'\\s]+)[\"']?"
     ]
   }
   ```

### Policy Configuration

Create `.renovaterc.json` for repository-specific overrides:

```json
{
  "extends": ["config:base"],
  "schedule": ["before 6am on monday"],
  "labels": ["dependencies", "automated"],
  "assignees": ["@traider-devops-team"],
  "reviewers": ["@traider-security-team"]
}
```

## 🚨 Incident Response

### Failed Renovate Execution

1. **Check Workflow Logs**:

   ```bash
   gh run list --workflow="Renovate Dependency Management"
   gh run view <run-id> --log
   ```

2. **Common Issues**:
   - Token expiration
   - Rate limiting
   - Configuration errors
   - Network connectivity

3. **Recovery Actions**:
   ```bash
   # Re-run with debug logging
   gh workflow run "Renovate Dependency Management" \
     --field log_level=debug \
     --field dry_run=true
   ```

### Problematic Updates

1. **Revert PR**:

   ```bash
   # Close problematic PR
   gh pr close <pr-number>

   # Add to ignore list temporarily
   echo "Temporarily ignoring package due to issues" >> .renovaterc.json
   ```

2. **Update Configuration**:
   ```json
   {
     "packageRules": [
       {
         "matchPackageNames": ["problematic-package"],
         "enabled": false,
         "description": "Temporarily disabled due to compatibility issues"
       }
     ]
   }
   ```

## 🔄 Maintenance

### Token Rotation (Every 90 Days)

1. **Generate New Token**:
   - Follow token creation process
   - Update repository secrets
   - Test with dry run

2. **Validation**:
   ```bash
   # Test new token
   curl -H "Authorization: token NEW_TOKEN" \
        "https://api.github.com/repos/your-org/traider"
   ```

### Configuration Updates

1. **Monthly Reviews**:
   - Review ignored packages
   - Update stability periods
   - Assess automerge rules

2. **Quarterly Audits**:
   - Comprehensive configuration review
   - Performance optimization
   - Security policy updates

### Dependency Health Monitoring

```bash
# Check dependency health
npm audit
snyk test --all-projects

# Review outdated packages
npm outdated
pip list --outdated
```

## 📚 Best Practices

### Development Workflow

1. **Monitor Dependency Dashboard**: Check weekly for pending updates
2. **Review PRs Promptly**: Don't let dependency PRs accumulate
3. **Test Thoroughly**: Especially for trading-critical dependencies
4. **Coordinate with Team**: Communicate about major updates

### Security Considerations

- **Never ignore security updates** without security team approval
- **Review major version updates** carefully for breaking changes
- **Monitor for supply chain attacks** in dependency updates
- **Validate dependencies** from trusted sources only

### Performance Optimization

```json
{
  "prConcurrentLimit": 5,
  "prHourlyLimit": 2,
  "branchConcurrentLimit": 10,
  "hostRules": [
    {
      "matchHost": "github.com",
      "concurrentRequestLimit": 10
    }
  ]
}
```

## 🔗 Integration with Other Tools

### GitHub Actions

Renovate updates GitHub Actions automatically:

```json
{
  "packageRules": [
    {
      "matchManagers": ["github-actions"],
      "automerge": true,
      "automergeType": "pr"
    }
  ]
}
```

### Dependabot Integration

Renovate can replace or complement Dependabot:

```yaml
# .github/dependabot.yml
version: 2
updates: [] # Disabled in favor of Renovate
```

### Docker Integration

```json
{
  "docker": {
    "enabled": true,
    "major": {
      "enabled": false
    }
  }
}
```

## 📞 Support & Troubleshooting

### Common Issues

1. **Rate Limiting**:

   ```json
   {
     "hostRules": [
       {
         "matchHost": "api.github.com",
         "concurrentRequestLimit": 1
       }
     ]
   }
   ```

2. **Large Repositories**:

   ```json
   {
     "repositories": ["your-org/traider"],
     "autodiscoverFilter": "your-org/traider"
   }
   ```

3. **Configuration Validation**:
   ```bash
   # Validate configuration
   renovate-config-validator renovate.json
   ```

### Getting Help

- **Renovate Documentation**: [docs.renovatebot.com](https://docs.renovatebot.com)
- **Community Support**: [github.com/renovatebot/renovate/discussions](https://github.com/renovatebot/renovate/discussions)
- **Configuration Help**: Use the dependency dashboard for quick fixes

## 🎯 Roadmap

### Planned Enhancements

- [ ] AI-powered dependency risk assessment
- [ ] Integration with trading performance metrics
- [ ] Custom update strategies for different market conditions
- [ ] Advanced conflict resolution
- [ ] Real-time dependency vulnerability monitoring

### Version History

- **v1.0**: Initial Renovate integration with basic dependency management
- **v1.1**: Added security-focused update prioritization
- **v1.2**: Enhanced CI/CD integration and monitoring
- **v1.3**: Advanced configuration management and custom managers
- **v1.4**: Trading-aware scheduling and stability controls

---

_This document is part of the TRAIDER V1 infrastructure framework. For questions or updates, contact the DevOps team._
