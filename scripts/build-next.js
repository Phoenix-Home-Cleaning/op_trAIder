#!/usr/bin/env node
// Wrapper script to ensure our Windows readlink patch is pre-loaded before Next's CLI spins up.

import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';

// Always preload the shim via NODE_OPTIONS so the child Node process inherits it.
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const shimPath = path.resolve(__dirname, 'win-readlink-shim.cjs');

const env = { ...process.env };
const requireFlag = `--require ${shimPath}`;

if (env.NODE_OPTIONS) {
  if (!env.NODE_OPTIONS.includes(requireFlag)) {
    env.NODE_OPTIONS += ` ${requireFlag}`;
  }
} else {
  env.NODE_OPTIONS = requireFlag;
}

const nextCli = path.resolve(__dirname, '../node_modules/next/dist/bin/next');

const result = spawnSync(process.execPath, [
  '--require',
  shimPath,
  nextCli,
  'build',
], {
  stdio: 'inherit',
  env,
  shell: false,
});

process.exit(result.status ?? 1); 