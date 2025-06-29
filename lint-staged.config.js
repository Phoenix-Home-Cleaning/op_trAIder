module.exports = {
  // TypeScript and React files - Core trading logic
  '*.{ts,tsx}': [
    'eslint --fix --max-warnings 0',
    'prettier --write',
  ],

  // Configuration and data files
  '*.{json,md}': [
    'prettier --write',
  ],

  // Package files - dependency security (removed audit as it's handled in CI)
  'package*.json': [
    'prettier --write',
  ],
}; 