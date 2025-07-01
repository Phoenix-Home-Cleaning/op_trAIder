# ADR-009: Migration to Trivy for Unified Security Scanning

## Status

Accepted - 2024-12-XX

## Context

TRAIDER V1 initially implemented security scanning using multiple tools:

- **Snyk**: Dependency vulnerability scanning, container scanning, and IaC analysis
- **GitLeaks**: Secret detection in source code and git history

This multi-tool approach introduced several challenges:

### Problems with Previous Approach

1. **Licensing Complexity**:
   - Snyk requires API tokens and paid subscriptions for advanced features
   - GitLeaks requires organization-level licenses for GitHub enterprise features
   - Licensing costs and setup complexity hindering development velocity

2. **Tool Coordination**:
   - Multiple workflows and configurations to maintain
   - Different output formats requiring separate processing
   - Increased CI/CD complexity and execution time

3. **Coverage Gaps**:
   - Snyk limited to specific language ecosystems
   - GitLeaks focused only on secrets, not broader security issues
   - No unified reporting or quality gates

4. **Operational Overhead**:
   - Multiple API tokens and secrets to manage
   - Different update cycles and maintenance requirements
   - Fragmented security findings across tools

## Decision

We will migrate to **Trivy** as the unified security scanning solution, replacing both Snyk and GitLeaks.

### Trivy Advantages

1. **100% Open Source**: No licensing costs or API token requirements
2. **Comprehensive Coverage**: Vulnerabilities, secrets, misconfigurations, and licenses
3. **Broad Ecosystem Support**: 30+ language ecosystems vs Snyk's limited set
4. **Enhanced Secret Detection**: 190+ built-in patterns vs GitLeaks' standard set
5. **Native GitHub Integration**: SARIF output for GitHub Security tab
6. **High Performance**: Parallel scanning and efficient caching
7. **Single Tool Maintenance**: Unified configuration and updates

## Implementation

### Migration Strategy

1. **Workflow Replacement**:
   - Replace `.github/workflows/snyk-security.yml` with `.github/workflows/trivy-security.yml`
   - Update existing security workflows to use Trivy actions
   - Maintain quality gates and security thresholds

2. **Configuration Migration**:
   - Replace `.gitleaks.toml` and `.gitleaksignore` with `.trivyignore`
   - Update npm scripts from Snyk commands to Trivy equivalents
   - Remove Snyk API token dependencies

3. **Pre-commit Integration**:
   - Update Husky pre-commit hooks to use Trivy for secrets scanning
   - Implement staged-file scanning for performance optimization
   - Maintain commit-blocking behavior for security violations

4. **Documentation Updates**:
   - Create comprehensive Trivy integration guide
   - Update security scanning documentation
   - Document migration process and troubleshooting

### Technical Implementation

#### New Trivy Workflow Features

```yaml
# Parallel scanning jobs
- trivy-vulnerability-scan
- trivy-secrets-scan
- trivy-config-scan
- trivy-license-scan

# Quality gates
CRITICAL_VULN_LIMIT: 0
HIGH_VULN_LIMIT: 5
SECRET_LIMIT: 0
```

#### NPM Scripts Migration

```json
// Before (Snyk)
"security:snyk": "snyk test --all-projects --severity-threshold=medium"

// After (Trivy)
"security:trivy": "trivy fs --scanners vuln,secret,config,license --format table --severity MEDIUM,HIGH,CRITICAL ."
```

#### Pre-commit Hook Enhancement

```bash
# Trivy secrets scan on staged files only
trivy fs --scanners secret --format table --quiet "$TEMP_DIR"
```

## Consequences

### Positive

1. **Cost Elimination**: Zero licensing costs for security scanning
2. **Simplified Operations**: Single tool to maintain and configure
3. **Enhanced Coverage**: Broader vulnerability and secret detection
4. **Improved Performance**: Faster execution with parallel scanning
5. **Better Integration**: Native GitHub Security tab integration
6. **Reduced Complexity**: Unified configuration and reporting

### Neutral

1. **Learning Curve**: Team needs to learn Trivy CLI and configuration
2. **Migration Effort**: One-time effort to update workflows and documentation

### Negative

1. **Tool Dependency**: Reliance on single open-source project
2. **Feature Parity**: Some Snyk-specific features may not have direct equivalents

### Risk Mitigation

1. **Backup Strategy**: Trivy has strong community support and active development
2. **Monitoring**: GitHub Security tab provides centralized vulnerability tracking
3. **Fallback Options**: Can re-introduce specialized tools if needed
4. **Documentation**: Comprehensive migration and troubleshooting guides

## Monitoring and Success Criteria

### Success Metrics

1. **Security Coverage**: Maintain or improve vulnerability detection rates
2. **Performance**: Reduce CI/CD execution time for security scans
3. **Developer Experience**: Faster local security scanning and clearer feedback
4. **Cost Savings**: Eliminate Snyk and GitLeaks licensing costs
5. **Operational Efficiency**: Reduce security tool maintenance overhead

### Monitoring Approach

1. **GitHub Security Tab**: Track vulnerability trends and resolution times
2. **CI/CD Metrics**: Monitor scan execution times and failure rates
3. **Developer Feedback**: Collect team feedback on new workflow experience
4. **Security Metrics**: Track mean time to vulnerability detection and resolution

## Implementation Timeline

- **Phase 1** (Day 1): Implement Trivy workflow and npm scripts
- **Phase 2** (Day 1): Update pre-commit hooks and remove old tools
- **Phase 3** (Day 1): Update documentation and team communication
- **Phase 4** (Week 1): Monitor and optimize based on initial usage

## Related ADRs

- ADR-003: Security Workflow GitLeaks and CodeQL Fixes (superseded)
- ADR-001: Initial Architecture Decision

## References

- [Trivy Official Documentation](https://aquasecurity.github.io/trivy/)
- [Trivy GitHub Actions](https://github.com/aquasecurity/trivy-action)
- [TRAIDER Security Integration Guide](../security/trivy-integration.md)

---

**Author**: TRAIDER Security Team  
**Date**: 2024-12-XX  
**Reviewers**: DevOps Team, Security Team  
**Status**: Implemented
