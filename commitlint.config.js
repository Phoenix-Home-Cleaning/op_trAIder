/**
 * @fileoverview Commitlint configuration for TRAIDER V1
 * @description Enforces conventional commit format for institutional-grade development
 */

export default {
  extends: ['@commitlint/config-conventional'],
  rules: {
    // Enforce conventional commit types
    'type-enum': [
      2,
      'always',
      [
        'feat',     // New feature or trading strategy
        'fix',      // Bug fix or trading issue resolution
        'docs',     // Documentation changes
        'style',    // Code style changes (formatting, etc.)
        'refactor', // Code refactoring without behavior change
        'perf',     // Performance improvements
        'test',     // Test additions or modifications
        'chore',    // Maintenance tasks
        'build',    // Build system or dependency changes
        'ci',       // CI/CD pipeline changes
        'revert',   // Reverting previous commits
      ],
    ],
    // Subject length limits
    'subject-max-length': [2, 'always', 100],
    'subject-min-length': [2, 'always', 3],
    'subject-case': [2, 'always', 'lower-case'],
    'subject-empty': [2, 'never'],
    'subject-full-stop': [2, 'never', '.'],
    
    // Header format
    'header-max-length': [2, 'always', 100],
    
    // Body and footer (optional but encouraged for complex changes)
    'body-leading-blank': [1, 'always'],
    'footer-leading-blank': [1, 'always'],
    
    // Scope validation for trading components
    'scope-enum': [
      1,
      'always',
      [
        // Frontend components
        'dashboard',
        'charts',
        'ui',
        'auth',
        'performance',
        'risk',
        'signals',
        'system',
        
        // Backend services
        'market-data',
        'signal-gen',
        'risk-engine',
        'executor',
        'portfolio',
        'ml',
        
        // Infrastructure
        'infrastructure',
        'ci',
        'deployment',
        'monitoring',
        'security',
        'database',
        
        // Development
        'tests',
        'docs',
        'scripts',
        'config',
        'deps',
      ],
    ],
  },
  // Custom prompt for interactive commits
  prompt: {
    questions: {
      type: {
        description: 'Select the type of change that you\'re committing:',
        enum: {
          feat: {
            description: 'A new feature or trading strategy',
            title: 'Features',
            emoji: '✨',
          },
          fix: {
            description: 'A bug fix or trading issue resolution',
            title: 'Bug Fixes',
            emoji: '🐛',
          },
          perf: {
            description: 'A code change that improves performance',
            title: 'Performance Improvements',
            emoji: '⚡️',
          },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
            emoji: '📦',
          },
          docs: {
            description: 'Documentation only changes',
            title: 'Documentation',
            emoji: '📚',
          },
          test: {
            description: 'Adding missing tests or correcting existing tests',
            title: 'Tests',
            emoji: '🚨',
          },
          chore: {
            description: 'Other changes that don\'t modify src or test files',
            title: 'Chores',
            emoji: '♻️',
          },
        },
      },
      scope: {
        description: 'What is the scope of this change (e.g. component or file name)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description: 'A BREAKING CHANGE commit requires a body. Please enter a longer description of the commit itself',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description: 'If issues are closed, the commit requires a body. Please enter a longer description of the commit itself',
      },
      issues: {
        description: 'Add issue references (e.g. "fix #123", "re #123".)',
      },
    },
  },
}; 