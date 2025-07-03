# ADR-014: Monorepo Tooling Package

| Status       | Date       | Supersedes | Superseded by |
| ------------ | ---------- | ---------- | ------------- |
| **Accepted** | 2025-07-03 | —          | —             |

## Context

The repository historically stored developer utilities as individual TypeScript files inside the root `scripts/` directory. Over time these utilities grew in size (some >600 LOC) and became difficult to test, reuse, and enforce versioning for.  
Notably, `scripts/validate-docs.ts` performs multi-phase documentation validation and is invoked by CI and pre-commit hooks. Keeping such a critical component as an ad-hoc script violates the project guideline of _modularity_ and makes dependency management elusive.

Key pain points:

1. **Lack of dependency isolation** – utilities implicitly rely on root-level devDependencies which may drift.
2. **Poor testability** – no dedicated package.json, cannot easily add unit tests or publish binaries.
3. **Console-logging noise** – pre-commit console-statement gate flagged legitimate logs inside scripts.
4. **Scalability** – adding more tooling scripts increases cognitive load in root namespace.

## Decision

We introduce a dedicated workspace package `@traider/tooling` under `packages/tooling/` managed via **npm workspaces**.

### Structure

```
packages/
  tooling/
    package.json   # versioned manifest, own deps
    src/
      validate-docs.ts  # migrated script (CLI entry)
```

- Root `package.json` now declares `"workspaces": ["packages/*"]` enabling monorepo tooling.
- The tooling package exposes a binary `validate-docs` mapped to `src/validate-docs.ts`.  
  Root scripts `docs:validate` and `docs:coverage` call the binary via tsx path until we pre-compile.
- Pre-commit console-statement check ignores `packages/tooling/` to allow intentional logging.

## Consequences

Positive:

- Utilities are versioned, testable, and can declare explicit dependencies (e.g., `glob`).
- Future scripts (complexity-analysis, benchmarks, etc.) can reside in the same package or sibling tooling packages.
- Cleaner root namespace; easier onboarding.
- Opens path to publish internal CLI (`npx traider`) if desired.

Negative / Trade-offs:

- Slightly more setup – workspace hoisting rules must be respected.
- Pre-commit script updated to call tsx path until we implement transpiled dist; minor overhead.

## Migration Plan

1. Move existing large scripts from `scripts/` into `packages/tooling/src/` incrementally.
2. Replace root `npm run <script>` invocations with workspace binaries.
3. Add unit tests inside `packages/tooling/tests/` (future work).
4. When stable, pre-build tooling with `tsx --build` and point bin to `dist/` for faster startup.

## Alternatives Considered

- **Keep scripts/ directory** – rejected due to scalability and dependency issues.
- **Separate repo** – increases maintenance overhead; workspace is simpler.
- **Nx / Turborepo** – may still be adopted, but base npm workspaces is the minimal enabler.

---

_Authors_: TRAIDER Architecture Guild
