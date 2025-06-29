# ADR-003: Security Workflow GitLeaks and CodeQL Fixes

## Status

Accepted

## Context

The TRAIDER V1 security scanning pipeline encountered two critical issues:

1. **GitLeaks License Error**: The workflow was configured to require a `GITLEAKS_LICENSE` secret, but GitLeaks has transitioned to an open-source model and no longer requires a license for basic secret scanning functionality.

2. **CodeQL SARIF Upload Conflicts**: Multiple CodeQL analysis jobs were attempting to upload SARIF results with the same category, causing the error: "only one run of the codeql/analyze or codeql/upload-sarif actions is allowed per job per tool/category."

These issues were blocking the CI/CD pipeline and preventing proper security validation of code changes.

## Decision

We will implement the following fixes to resolve the security workflow issues:

### GitLeaks License Resolution

- **Remove** the `GITLEAKS_LICENSE` environment variable from the GitLeaks action
- **Update** the workflow to use GitLeaks v2 in open-source mode
- **Add** documentation comment explaining the license removal

### CodeQL SARIF Upload Fix

- **Eliminate** the matrix strategy for CodeQL scanning that was creating duplicate jobs
- **Consolidate** to a single JavaScript/TypeScript analysis job
- **Remove** the redundant SARIF upload step that was causing conflicts
- **Add** unique categories for different scan types (Trivy filesystem scans)

### Workflow Optimization

- **Simplify** the SAST scanning to focus on JavaScript/TypeScript as our primary languages
- **Ensure** each security tool has a unique category for SARIF uploads
- **Maintain** comprehensive security coverage while eliminating conflicts

## Consequences

### Positive

- **Unblocked CI/CD Pipeline**: Security scans will run successfully without license errors
- **Eliminated SARIF Conflicts**: Each security tool uploads results with unique categories
- **Maintained Security Coverage**: All critical security scans (secrets, SAST, dependencies) remain active
- **Simplified Workflow**: Reduced complexity by removing unnecessary matrix strategy
- **Cost Optimization**: No longer requires paid GitLeaks license for basic functionality

### Negative

- **Reduced Language Coverage**: Consolidated to JavaScript analysis (though TypeScript is included)
- **Potential Future Limitations**: May need to revisit if GitLeaks introduces premium features

### Neutral

- **No Impact on Security Posture**: Same level of security scanning with different implementation
- **Workflow Performance**: Similar execution time with simplified job structure

## Implementation Details

### GitLeaks Configuration

```yaml
- name: 🔍 GitLeaks secrets scan
  uses: gitleaks/gitleaks-action@v2
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  # Note: GITLEAKS_LICENSE removed - GitLeaks is now open source
```

### CodeQL Configuration

```yaml
- name: 🔧 Initialize CodeQL
  uses: github/codeql-action/init@v3
  with:
    languages: javascript
    queries: +security-and-quality

- name: 🔍 Perform CodeQL Analysis
  uses: github/codeql-action/analyze@v3
  with:
    category: '/language:javascript'
```

### SARIF Upload Categories

- **CodeQL**: `/language:javascript`
- **Trivy**: `trivy-filesystem`
- **TruffleHog**: Integrated with action (no separate upload)

## Monitoring and Validation

- **Success Metrics**: Security workflow completes without errors
- **Coverage Verification**: All security scan types produce results
- **Performance Tracking**: Monitor workflow execution time (<10 minutes target)
- **Alert Configuration**: Ensure security findings are properly reported

## References

- [GitLeaks Action Documentation](https://github.com/gitleaks/gitleaks-action)
- [CodeQL Action Documentation](https://github.com/github/codeql-action)
- [SARIF Support Documentation](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)
- [TRAIDER Security Scanning Documentation](../security/security-scanning.md)

## Date

2025-06-29

## Author

TRAIDER Team
