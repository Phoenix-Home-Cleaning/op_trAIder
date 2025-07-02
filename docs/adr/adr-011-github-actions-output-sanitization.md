# ADR-011: GitHub Actions Output Format Sanitization

## Status

Accepted

## Context

The TRAIDER V1 CI/CD pipeline was experiencing critical failures in the coverage threshold enforcement step with the following error:

```
Error: Unable to process file command 'output' successfully.
Error: Invalid format '0.0'
```

### Root Cause Analysis

The issue was caused by malformed GitHub Actions output files when our trading coverage calculator script returned multi-line output:

1. **Script Execution**: When `python scripts/calculate-trading-coverage.py --threshold 90.0` exits with non-zero status (coverage < 90% or parsing errors), the fallback `|| echo "0.0"` executes
2. **Multi-line Output**: This results in two lines being captured:
   ```
   85.42    ← actual coverage from script
   0.0      ← fallback echo
   ```
3. **Malformed Output File**: The entire multi-line string gets written to `$GITHUB_OUTPUT`:
   ```
   trading-coverage=85.42
   0.0                    ← invalid line without key=value format
   ```
4. **GitHub Actions Parsing Error**: The runner fails to parse the malformed output file

### Business Impact

- **Deployment Blocking**: CI/CD pipeline failures prevent legitimate deployments
- **False Negatives**: Valid coverage reports were being rejected due to format issues
- **Developer Productivity**: Engineers were blocked by infrastructure issues rather than code quality
- **Risk to Trading Operations**: Delayed deployments could impact trading system updates

## Decision

Implement a robust output sanitization strategy that:

1. **Captures Raw Output Safely**: Use `|| true` instead of `|| echo "0.0"` to prevent multi-line output
2. **Sanitizes Values**: Extract only the first line and filter to numeric characters
3. **Provides Fallbacks**: Gracefully handle empty or malformed responses
4. **Maintains Business Logic**: Preserve threshold enforcement and error reporting

### Implementation

```yaml
# Before (problematic)
TRADING_COVERAGE=$(python scripts/calculate-trading-coverage.py --threshold 90.0 2>/dev/null || echo "0.0")
echo "trading-coverage=${TRADING_COVERAGE}" >> $GITHUB_OUTPUT

# After (sanitized)
RAW_TRADING_COVERAGE=$(python scripts/calculate-trading-coverage.py \
                         --threshold 90.0 2>/dev/null || true)
TRADING_COVERAGE=$(echo "${RAW_TRADING_COVERAGE}" | head -n1 | tr -cd '0-9.')
if [ -z "${TRADING_COVERAGE}" ]; then
  TRADING_COVERAGE="0.0"
fi
echo "trading-coverage=${TRADING_COVERAGE}" >> $GITHUB_OUTPUT
```

## Consequences

### Positive

- **Eliminates CI Failures**: Prevents malformed GitHub Actions output files
- **Maintains Quality Gates**: Preserves 90% trading logic coverage requirement
- **Improves Reliability**: Makes CI/CD pipeline more resilient to edge cases
- **Future-Proof**: Works with current and future GitHub Actions versions
- **Auditable**: Clear separation of data capture and business logic

### Negative

- **Slightly More Complex**: Additional shell logic for sanitization
- **Potential Data Loss**: Only first line of multi-line output is captured (acceptable trade-off)

### Neutral

- **No Performance Impact**: Sanitization adds negligible overhead
- **Backward Compatible**: Existing coverage thresholds and logic unchanged

## Compliance

### Institutional Standards Met

- **Reliability**: 99.9% CI/CD pipeline availability target maintained
- **Auditability**: All coverage decisions remain traceable
- **Risk Management**: Defensive coding prevents deployment pipeline failures
- **Documentation**: ADR provides decision rationale for future reference

### Monitoring

- **Metric**: `ci.coverage_enforcement.success_rate`
- **Alert**: Pipeline failures in coverage step
- **SLA**: <1% false failure rate due to format issues

## Implementation Notes

### Testing Strategy

1. **Unit Tests**: Validate shell sanitization logic with various inputs
2. **Integration Tests**: Test full coverage workflow with edge cases
3. **Chaos Testing**: Simulate malformed coverage files and script failures

### Rollback Plan

If issues arise, the change can be reverted by replacing the sanitization block with the original single-line assignment. The fix is isolated to the coverage enforcement step.

### Future Improvements

1. **Structured Output**: Consider JSON output from coverage calculator
2. **Validation**: Add schema validation for coverage data
3. **Monitoring**: Track sanitization effectiveness metrics

## References

- [GitHub Actions Output Commands](https://docs.github.com/en/actions/using-workflows/workflow-commands-for-github-actions#setting-an-output-parameter)
- [TRAIDER CI/CD Pipeline Documentation](../infrastructure/ci-cd-pipeline.md)
- [Trading Coverage Calculator](../../scripts/calculate-trading-coverage.py)

## Author

TRAIDER Engineering Team

## Date

2025-01-27
