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

echo "🔑 Checking for hardcoded passwords..."

for file in "$@"; do
  # Skip files in any 'tests/' directory
  if [[ "$file" == *"tests/"* ]]; then
    continue
  fi

  # Check for "password =" with optional whitespace. -l prints the filename.
  # We use `grep ... || true` to prevent the script from exiting if grep finds no match (as grep would return exit code 1).
  if grep -l -E 'password\s*=' "$file" > /dev/null; then
    echo "❌ ERROR: Hardcoded password pattern 'password =' found in '$file'."
    echo "   Please use environment variables or a secure secret management solution."
    exit 1
  fi
done

echo "✅ No hardcoded passwords found."
exit 0 