# ADR-020: Windows `fs.readlink*` Shim to Mitigate Node 22 `EISDIR` Regression

Date: 2025-07-05

## Status
Accepted

## Context
Starting with **Node.js 22** the Windows implementation of
`fs.readlinkSync()` (and its async counterparts) changed behaviour:

* When the target path is a **directory** it now throws
  `EISDIR: illegal operation on a directory, readlink …` instead of the
  historical `EINVAL` (`EINVAL` is what Webpack, Next.js and a large
  part of the ecosystem expect when probing if a file is a symlink).
* Webpack uses `readlinkSync()` during its resolver phase.  The new
  `EISDIR` propagates, aborting the compilation before user code is
  executed.  This breaks every Windows build on Node 22+ (see
  `next build` crash inside `node_modules/next/dist/pages/_app.js`).

Waiting for upstream fixes (Node, Webpack, Next) would block Phase-1
MVP development.  A surgical patch is therefore required.

## Decision
1. **Global shim** – Implement a one-time patch that monkey-patches
   `fs.readlinkSync`, `fs.readlink` and `fs.promises.readlink` _only on
   Windows_.  If they throw `EISDIR`, the shim returns the original
   path string – exactly how Webpack treated `EINVAL` pre-Node 22.  All
   other errors propagate unchanged.
2. **Pre-load via `NODE_OPTIONS`** – Create `scripts/build-next.js`
   which injects `--require <abs\win-readlink-shim.js>` into
   `NODE_OPTIONS` and then executes the local `next build`.  Every
   subprocess spawned by Next.js inherits the shim automatically
   (worker processes, Babel transforms, etc.).
3. **Wrapper replaces build script** – `package.json → build:next`
   now calls the wrapper, ensuring local dev, CI and Docker builds all
   enjoy the patch with zero manual steps.
4. **Remove in-file patches** – The temporary patch that had been added
   to `apps/frontend/next.config.mjs` has been removed to avoid duplicate
   monkey-patching and resolver recursion.
5. **Scope-limited & removable** – Linux/macOS code paths remain
   untouched.  Once upstream libraries resolve the regression the shim
   and wrapper can be deleted and `build:next` reverted to the original
   command.

## Consequences
* Windows builds and CI pipelines are unblocked while staying on the
  latest Node LTS.
* No runtime performance impact on non-Windows hosts.
* Slightly longer cold-start (one extra `require`) on Windows only.
* Future maintainers must remember to strip the shim when it becomes
  obsolete. 