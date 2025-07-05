# ADR-018: Typed Coverage Enforcement and Ratchet Policy

## Status

Proposed

## Context

We aim to continuously improve Python type coverage in the TRAIDER backend to reduce production risk and accelerate refactoring velocity. Static type checks catch issues early, improving uptime (99.9% KPI) and protecting P&L.

## Decision

1. Create `mypy.ini` to exclude generated code (migrations, snapshots) and enforce strict mode.
2. Enforce a ratcheting minimum threshold (starting at 35%) via CI (`scripts/check_mypy_coverage.py`).
3. Adopt SQLAlchemy 2.0 ORM typing (`Mapped[...]` and `mapped_column`) for core models.
4. Add a pre-commit hook to run mypy on staged files and prevent regressions.
5. Increment threshold by 5% each sprint until business-critical packages reach ≥80%.
6. Push typed coverage metrics to Prometheus Pushgateway for long-term monitoring.

## Consequences

- CI will block any regression in typed coverage, ensuring continuous discipline.
- Gradual annotation effort avoids big-bang rewrites.
- Improved type safety reduces production incidents and MTTR.
- Developer confidence in refactorings grows with type support.

## References

- `scripts/check_mypy_coverage.py`
- CI Workflow: `.github/workflows/ci.yml`
- SQLAlchemy 2.0 typing docs 