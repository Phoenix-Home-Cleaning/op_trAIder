# ADR-003: Security Workflow Migration to Trivy (Superseded)

## Status

**SUPERSEDED** - 2024-12-XX by Trivy migration

This ADR has been superseded by the migration to Trivy as the unified security scanner.

## Context

The TRAIDER V1 security scanning pipeline encountered multiple critical issues:

1. **GitLeaks License Error**: The workflow was initially configured to require a `GITLEAKS_LICENSE` secret. While GitLeaks has an open-source version, GitHub organizations require a license key for advanced features and organization-level scanning.

2. **CodeQL SARIF Upload Conflicts**: Multiple CodeQL analysis jobs were attempting to upload SARIF results with the same category, causing the error: "only one run of the codeql/analyze or codeql/upload-sarif actions is allowed per job per tool/category."

3. **TruffleHog BASE/HEAD Commit Issues**: TruffleHog was failing when BASE and HEAD commits were the same, particularly on initial commits or when `github.event.before` was not available.

4. **CodeQL Default Setup Conflicts**: Advanced CodeQL configuration was conflicting with GitHub's default CodeQL setup, causing "cannot be processed when the default setup is enabled" errors.

These issues were blocking the CI/CD pipeline and preventing proper security validation of code changes.

## Decision

We will implement the following fixes to resolve the security workflow issues:

### GitLeaks License Resolution

- **Restore** the `GITLEAKS_LICENSE` environment variable for organization-level scanning
- **Configure** GitHub Secrets to store the license key securely
- **Add** .env.example file with placeholder for local development

### CodeQL SARIF Upload Fix

- **Eliminate** the matrix strategy for CodeQL scanning that was creating duplicate jobs
- **Consolidate** to a single JavaScript/TypeScript analysis job
- **Remove** the redundant SARIF upload step that was causing conflicts
- **Add** unique categories for different scan types (Trivy filesystem scans)

### TruffleHog Configuration Fix

- **Add conditional logic** to handle cases where BASE and HEAD commits are the same
- **Implement fallback scanning** for initial commits using full repository scan
- **Use proper commit references** with validation for null/zero commits

### CodeQL Configuration Replacement

- **Replace CodeQL workflow** with ESLint security analysis to avoid default setup conflicts
- **Leverage GitHub's default CodeQL setup** for SARIF uploads and security scanning
- **Implement ESLint-based SAST** with security-focused rules and reporting

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
    GITLEAKS_LICENSE: ${{ secrets.GITLEAKS_LICENSE }}
  # Note: Organization-level GitLeaks requires license key
```

### TruffleHog Configuration

```yaml
- name: 🔐 Run TruffleHog secrets scan
  uses: trufflesecurity/trufflehog@main
  if: github.event.before && github.event.before != '0000000000000000000000000000000000000000'
  with:
    path: ./
    base: ${{ github.event.before }}
    head: ${{ github.sha }}
    extra_args: --debug --only-verified

- name: 🔐 Run TruffleHog full scan (fallback)
  uses: trufflesecurity/trufflehog@main
  if: github.event.before == '0000000000000000000000000000000000000000' || !github.event.before
  with:
    path: ./
    extra_args: --debug --only-verified
```

### ESLint Security Analysis Configuration

```yaml
- name: 🔍 ESLint Security Analysis
  run: |
    # Run ESLint with security rules
    npx eslint . --ext .ts,.tsx,.js,.jsx --format json --output-file eslint-results.json || true

    # Process and validate security-related errors
    SECURITY_ERRORS=$(jq '[.[] | .messages[] | select(.ruleId | test("security"))] | length' eslint-results.json)
    if [ "$SECURITY_ERRORS" -gt 0 ]; then
      echo "::error::Security-related ESLint errors found: $SECURITY_ERRORS"
      exit 1
    fi

- name: ℹ️ CodeQL Notice
  run: |
    echo "::notice::CodeQL analysis is handled by GitHub's default setup. View results in the Security tab."
```

### Security Analysis Tools

- **CodeQL**: Handled by GitHub's default setup (automatic SARIF upload)
- **ESLint**: Custom security analysis with artifact upload
- **Trivy**: `trivy-filesystem` SARIF category
- **TruffleHog**: Integrated with action (no separate upload)
- **GitLeaks**: Integrated with action (no separate upload)

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
