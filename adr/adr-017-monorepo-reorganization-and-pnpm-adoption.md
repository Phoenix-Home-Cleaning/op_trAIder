# ADR-017: Monorepo Reorganization and pnpm Adoption

**Status**: Accepted
**Date**: 2025-07-05
**Deciders**: TRAIDER Team
**Technical Story**: N/A

---

## Context

The project's root directory was cluttered with a mix of source code, configuration, scripts, and documentation, making it difficult to navigate and scale. The `npm` package manager also caused persistent `EISDIR` symlink errors on Windows, even with Developer Mode enabled, due to the exFAT filesystem, blocking all installation and validation efforts. This necessitated a dual-pronged approach: reorganize the codebase into a standard monorepo structure and adopt a more robust package manager.

### Background
- Current situation
- Problem statement
- Constraints and requirements
- Stakeholders affected

### Technical Context
- Current architecture/implementation
- Performance considerations
- Security implications
- Operational impact

---

## Decision

We have implemented a full monorepo structure and migrated from `npm` to `pnpm`.

### Chosen Solution
1.  **Monorepo Structure**:
    -   `apps/`: Contains the core `frontend` (Next.js) and `backend` (FastAPI) applications.
    -   `services/`: Houses stand-alone microservices, starting with `market-data-service`.
    -   `packages/`: For shared libraries and tooling.
    -   `infra/`: Holds all infrastructure-as-code (Helm, Kubernetes, etc.).
    -   `config/`: Centralizes all environment and Docker configuration.
    -   `scripts/`: Contains all operational and utility scripts.
2.  **Package Manager**:
    -   Adopted `pnpm` as the primary package manager.
    -   Created a `.npmrc` file with `node-linker=hoisted` to resolve the exFAT symlink issue on the development environment.
    -   Removed `package-lock.json` in favor of `pnpm-lock.yaml`.

### Alternative Solutions Considered
1. **Option A**: Brief description and why it was rejected
2. **Option B**: Brief description and why it was rejected
3. **Option C**: Brief description and why it was rejected

---

## Consequences

### Positive Consequences
- **Improved Organization**: The new structure is logical, scalable, and aligns with industry best practices for monorepos.
- **Enhanced Developer Experience**: Clear separation of concerns makes the codebase easier to understand, navigate, and contribute to.
- **Resolved Installation Issues**: `pnpm` with the `hoisted` linker provides a stable, cross-platform installation process that works on all filesystems.
- **Faster Builds**: `pnpm`'s efficient dependency management can lead to faster installation and build times.

### Negative Consequences
- **Learning Curve**: Team members unfamiliar with `pnpm` will need a short ramp-up period.
- **CI/CD Adjustments**: All CI/CD workflows that used `npm` commands will need to be updated to use `pnpm`.

### Risks and Mitigation
- **Risk 1**: Description and mitigation strategy
- **Risk 2**: Description and mitigation strategy

---

## Implementation

### Action Items
- [ ] Task 1: Description and owner
- [ ] Task 2: Description and owner
- [ ] Task 3: Description and owner

### Timeline
- **Phase 1** (Week 1-2): Initial implementation
- **Phase 2** (Week 3-4): Testing and validation
- **Phase 3** (Week 5): Deployment and monitoring

### Success Criteria
- Measurable outcome 1
- Measurable outcome 2
- Performance benchmarks
- Acceptance criteria

---

## Monitoring and Review

### Metrics to Track
- Performance metrics
- Error rates
- User satisfaction
- Operational metrics

### Review Schedule
- **30 days**: Initial review of implementation
- **90 days**: Full impact assessment
- **6 months**: Long-term effectiveness review

---

## Related Decisions

### Supersedes
- [ADR-016: Previous decision title](link)

### Superseded by
- [ADR-016: Newer decision title](link)

### Related to
- [ADR-016: Related decision title](link)

---

## References

- [Technical documentation](link)
- [Research papers](link)
- [Industry best practices](link)
- [Performance benchmarks](link)

---

*This ADR follows the format established in [ADR-001: Architecture Decision Record Format](adr-001-adr-format.md)* 