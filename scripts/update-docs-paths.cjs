#!/usr/bin/env node
/* eslint-disable */
/**
 * Script to update documentation file references after monorepo reorganization.
 */
const fs = require('fs');
const path = require('path');
const { glob } = require('glob');

const projectRoot = path.resolve(__dirname, '..');
const pattern = path.join(projectRoot, 'docs', '**', '*.{md,mdx,yml,yaml}');

glob(pattern, (err, files) => {
  if (err) {
    console.error('Error finding doc files:', err);
    process.exit(1);
  }
  files.forEach((file) => {
    let content = fs.readFileSync(file, 'utf8');
    // Replace root app paths
    content = content.replace(/\(app\//g, '(apps/frontend/');
    content = content.replace(/\[app\//g, '[apps/frontend/');
    // Replace backend paths
    content = content.replace(/\(backend\//g, '(apps/backend/');
    content = content.replace(/\[backend\//g, '[apps/backend/');
    fs.writeFileSync(file, content, 'utf8');
    console.log(`Updated docs in ${file}`);
  });
}); 