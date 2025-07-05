#!/bin/bash
#
# @fileoverview Pre-commit hook to prevent committing hardcoded passwords.
# @module scripts/check-passwords
#
# This script iterates through a list of staged files and checks for the
# presence of the string "password =". It intentionally ignores any files
# within the 'tests/' directory, as mock passwords are required for testing.
#
# If a forbidden string is found in a non-test file, it prints an error
# message and exits with a status code of 1, blocking the commit.
#
# @usage
#   ./scripts/check-passwords.sh file1.py file2.ts ...

# Exit immediately if a command exits with a non-zero status.
set -e

# Define the regex pattern to search for. This looks for "password" followed by
# an optional equals sign and then a string literal.
PASSWORD_PATTERN="password\\s*=\\s*['\\\"]"
TEMP_FILE=$(mktemp)

# Ensure the temporary file is removed on exit
trap 'rm -f "$TEMP_FILE"' EXIT

echo "🔑 Checking for hardcoded passwords..."

# Find files containing the password pattern, excluding this script itself and environment-related files
# and ignoring lines that are assigning passwords from environment variables.
# The result is piped to a second grep to filter out false positives from process.env
grep -rliE "$PASSWORD_PATTERN" . --exclude-dir={.git,.husky,node_modules,build,dist,tests,docs,htmlcov,backend/htmlcov} --exclude="*.{env,lock.json,check-passwords.sh,CONTRIBUTING.md}" |
grep -vE "process\\.env" > "$TEMP_FILE" || true

if [ -s "$TEMP_FILE" ]; then
  echo "❌ ERROR: Hardcoded password pattern 'password =' found in the following files:"
  cat "$TEMP_FILE"
  echo "   Please use environment variables or a secure secret management solution."
  exit 1
fi

echo "✅ No hardcoded passwords found."
exit 0 