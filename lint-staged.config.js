export default {
  // Add a new check for hardcoded passwords in a wide range of text files
  '**/*.{ts,tsx,js,jsx,py,json,md,yml,yaml,toml,ini}': [
    'bash scripts/check-passwords.sh',
  ],

  // TypeScript and React files - Core trading logic (excluding .d.ts files)
  '*.{ts,tsx}': (filenames) => {
    const filteredFiles = filenames.filter(file => !file.endsWith('.d.ts'));
    if (filteredFiles.length === 0) {
      return [];
    }
    const eslintFiles = filteredFiles.filter(file => !file.includes('validate-docs.ts'));
    const eslintCommand = eslintFiles.length > 0 ? [`eslint --fix --max-warnings 0 ${eslintFiles.join(' ')}`] : [];
    
    return [
      ...eslintCommand,
      `prettier --write ${filteredFiles.join(' ')}`,
    ];
  },

  // Configuration and data files
  '*.{json,md}': [
    'prettier --write',
  ],

  // Package files - dependency security (removed audit as it's handled in CI)
  'package*.json': [
    'prettier --write',
  ],
}; 