#!/usr/bin/env node
/* eslint-disable */
/**
 * Script to update test import paths after monorepo reorganization.
 */
const fs = require('fs');
const path = require('path');
const { glob } = require('glob');

const projectRoot = path.resolve(__dirname, '..');
// Match all TypeScript and TSX test files under tests directory
const pattern = path.join(projectRoot, 'tests', '**', '*.{ts,tsx}');

glob(pattern, (err, files) => {
  if (err) {
    console.error('Error finding test files:', err);
    process.exit(1);
  }
  files.forEach((file) => {
    let content = fs.readFileSync(file, 'utf8');
    // Replace '../../../app/' with '../../../apps/frontend/app/'
    content = content.replace(/(\.\.\/){3}app\//g, '../../../apps/frontend/app/');
    // Replace '../../app/' with '../../apps/frontend/app/'
    content = content.replace(/(\.\.\/){2}app\//g, '../../apps/frontend/app/');
    // Replace '../../middleware' with '../../apps/frontend/middleware'
    content = content.replace(/(\.\.\/){2}middleware/g, '../../apps/frontend/middleware');
    // Replace two-up auth import from app/lib/auth
    content = content.replace(/(\.\.\/){2}app\/lib\/auth\//g, '../../apps/frontend/lib/auth/');
    fs.writeFileSync(file, content, 'utf8');
    console.log(`Updated imports in ${file}`);
  });
});
 