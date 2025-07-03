#!/usr/bin/env tsx
/**
 * @fileoverview Back-compat wrapper for documentation validation.
 * @module scripts/validate-docs
 *
 * @description
 * Delegates to the real implementation in
 * `packages/tooling/src/validate-docs.ts`.  Added to prevent CI
 * failures after the tooling extraction (ADR-014) without forcing
 * immediate workflow changes.
 *
 * @risk LOW – read-only wrapper.
 * @author TRAIDER Team
 * @since 2025-07-03
 */
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const target = resolve(
  dirname(fileURLToPath(import.meta.url)),
  '..',
  'packages',
  'tooling',
  'src',
  'validate-docs.ts'
);

await import(target);
