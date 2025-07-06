# ADR-012: CodeQL and SonarQube Workflow Configuration Fixes

## Status

Accepted

## Context

The code quality workflow was failing due to two critical configuration issues:

1. **CodeQL Conflict**: The repository had both GitHub's "Default setup" CodeQL enabled and a custom CodeQL workflow, causing SARIF upload conflicts with the error: "CodeQL analyses from advanced configurations cannot be processed when the default setup is enabled."

2. **SonarQube Connection Failure**: The SonarQube analysis was failing with "Failed to connect to localhost:9000" because the workflow was trying to connect to a local SonarQube instance that didn't exist, and the required secrets were not properly configured.

## Decision

We will:

1. **Remove duplicate CodeQL analysis** by eliminating the custom CodeQL steps from our workflow, relying solely on GitHub's organization-mandated default setup.

2. **Configure SonarCloud integration** by:
   - Using SonarCloud.io instead of a local SonarQube instance
   - Properly configuring GitHub repository secrets for authentication
   - Updating project configuration to match the correct organization and repository

3. **Enhance error handling** by adding validation steps to ensure required secrets are present before attempting analysis.

## Implementation

### CodeQL Changes

- Removed `github/codeql-action/init@v3`, `github/codeql-action/autobuild@v3`, and `github/codeql-action/analyze@v3` steps from the `advanced-security-scan` job
- Renamed the job to clarify it handles other security tools (Semgrep, dependency scanning) but not CodeQL
- Added explanatory comments about relying on GitHub's default setup

### SonarQube Changes

- Updated `sonar-project.properties` with correct project key: `Phoenix-Home-Cleaning_op_trAIder`
- Updated organization to: `phoenix-home-cleaning`
- Added backend Python source analysis
- Added validation step to check for required secrets before running analysis
- Simplified configuration by using existing properties file instead of generating inline

### Required Secrets

The following GitHub repository secrets must be configured:

- `SONAR_TOKEN`: User token from SonarCloud with "Execute Analysis" permission
- `SONAR_HOST_URL`: Set to `https://sonarcloud.io`

## Consequences

### Positive

- Eliminates CI failures due to conflicting CodeQL configurations
- Provides reliable SonarQube analysis through SonarCloud
- Maintains comprehensive security scanning coverage
- Adds proper error handling and validation
- Preserves all existing quality gates and thresholds

### Negative

- Requires manual setup of SonarCloud project and secrets
- Slightly less control over CodeQL configuration (using organization defaults)
- Dependency on external SonarCloud service

## Compliance

This change maintains institutional-grade standards by:

- Preserving all security scanning capabilities
- Maintaining audit logging and quality metrics
- Ensuring proper authentication and access controls
- Following principle of least privilege for CI/CD operations

## Monitoring

- CI workflow success/failure rates
- SonarQube quality gate pass/fail metrics
- CodeQL security alert generation and resolution
- Coverage and quality metric trends

## Rollback Plan

If issues arise:

1. Revert workflow changes to restore previous CodeQL steps
2. Temporarily disable SonarQube analysis step
3. Use local SonarQube container if SonarCloud is unavailable

## References

- [GitHub CodeQL Documentation](https://docs.github.com/en/code-security/code-scanning/automatically-scanning-your-code-for-vulnerabilities-and-errors/about-code-scanning)
- [SonarCloud Documentation](https://docs.sonarcloud.io/)
- [TRAIDER Infrastructure Documentation](../infrastructure/code-quality-pipeline.md)
