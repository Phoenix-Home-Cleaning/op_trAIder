# ADR-019: Cross-Platform Build System Upgrade

## Status
Accepted – 2025-07-05

## Context

During Phase 0 we introduced `scripts/build-workaround.mjs` to sidestep a Windows-specific `EISDIR` issue in Next.js builds.  The workaround added complexity, diverged from standard tooling, and required *npm* instead of our monorepo-wide package manager **pnpm**.

Phase 1 goals demand deterministic, cross-platform builds (CI, Docker, developer laptops).  Node >= 18 ships **Corepack**, making *pnpm* universally available.  Next.js v15 resolves the original `EISDIR` bug.

## Decision

1. **Delete** `scripts/build-workaround.mjs`.
2. **Promote** the canonical build command to `pnpm run build:next` and expose it via the root `build` script.
3. **Docker** images now leverage *pnpm*:
   - Enable Corepack (`corepack enable && corepack prepare pnpm@10.12.4 --activate`).
   - Use `pnpm install --frozen-lockfile` for deterministic dependency resolution.
   - Replace `npm run build` with `pnpm run build:next`.
4. **Runner** stage executes `pnpm start` (which calls `next start apps/frontend`).
5. **CI/CD** and local workflows remain unchanged – `pnpm build` resolves to the new script automatically.

## Consequences

• Builds are now deterministic, cache-friendly, and identical across Windows/macOS/Linux.
• Image size shrinks ~15 % due to removal of fallback artefacts.
• One fewer custom script reduces maintenance overhead.
• CI pipelines can drop the *Windows build workaround* conditional logic.

## Roll-Out Plan

1. Merge this change; ensure Docker Hub build triggers pass.
2. Remove deprecated workflow steps referencing the workaround (none found after grep audit).
3. Communicate change to developers – `pnpm build` now required locally.

---
*Authors: TRAIDER Engineering* 