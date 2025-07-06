#!/usr/bin/env node
// Wrapper script to ensure our Windows readlink patch is pre-loaded before Next's CLI spins up.

import path from 'path';
import { fileURLToPath } from 'url';
import { spawnSync } from 'child_process';
import fs from 'fs';

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

// Run build and capture output for detailed logging
const result = spawnSync(
  process.execPath,
  [
    '--require',
    shimPath,
    nextCli,
    'build',
    path.resolve(__dirname, '../apps/frontend'),
  ],
  {
    stdio: 'pipe', // capture for logging
    env,
    shell: false,
    encoding: 'utf-8',
  },
);

// Ensure logs directory exists
const logsDir = path.resolve(__dirname, '../logs');
if (!fs.existsSync(logsDir)) {
  fs.mkdirSync(logsDir, { recursive: true });
}

// Write detailed build log with timestamp
const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
const logFilePath = path.join(logsDir, `next-build-${timestamp}.log`);
fs.writeFileSync(logFilePath, `${result.stdout ?? ''}\n${result.stderr ?? ''}`);

// Stream output to parent process for CI visibility
process.stdout.write(result.stdout ?? '');
process.stderr.write(result.stderr ?? '');

process.exit(result.status ?? 1); 