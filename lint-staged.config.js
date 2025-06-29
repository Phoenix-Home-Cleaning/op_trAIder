module.exports = {
  // TypeScript and React files - Core trading logic with comprehensive checks
  '*.{ts,tsx}': [
    'eslint --fix --max-warnings 0',
    'prettier --write',
    () => 'npm run test:unit -- --run --reporter=verbose',
  ],

  // Trading service files - Require test coverage
  'app/lib/services/*.ts': [
    'eslint --fix --max-warnings 0',
    'prettier --write',
    () => 'npm run test:unit -- --coverage --run',
  ],

  // Configuration and documentation files
  '*.{json,md}': [
    'prettier --write',
  ],

  // Package files - dependency management
  'package*.json': [
    'prettier --write',
    () => 'npm audit --audit-level moderate',
  ],

  // Python files (backend trading services)
  '*.py': [
    () => 'python -m black --check .',
    () => 'python -m flake8 --max-line-length=100',
    () => 'python -m mypy --ignore-missing-imports',
  ],

  // Environment and config files - security check
  '*.{env,env.*}': [
    () => 'echo "⚠️  Environment files detected - ensure no secrets committed"',
  ],
}; 