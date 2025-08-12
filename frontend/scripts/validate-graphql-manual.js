#!/usr/bin/env node

/**
 * Manual GraphQL Validation Script
 *
 * This script can be run manually to validate GraphQL schema and operations.
 * It's not part of pre-commit hooks for faster development experience.
 *
 * Usage: yarn validate-graphql-manual
 */

import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

console.log('🔍 Manual GraphQL Validation');
console.log('============================\n');

try {
  // Check if API server is running
  console.log('1. Checking API server connection...');
  try {
    const response = await fetch('http://localhost:5000/graphql', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: '{ __schema { types { name } } }' }),
    });

    if (response.ok) {
      console.log('   ✅ API server is running');
    } else {
      throw new Error(`HTTP ${response.status}`);
    }
  } catch {
    console.log('   ❌ API server is not running');
    console.log(
      '   💡 Start the API server: cd api && python -m uvicorn src.main:app --reload --port 5000'
    );
    process.exit(1);
  }

  // Run schema validation
  console.log('\n2. Running GraphQL schema validation...');
  execSync('yarn validate-schema', {
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit',
  });

  // Run GraphQL operations test
  console.log('\n3. Running GraphQL operations test...');
  execSync('yarn test:graphql-operations', {
    cwd: path.join(__dirname, '..'),
    stdio: 'inherit',
  });

  console.log('\n✅ All GraphQL validations passed!');
  console.log('\n💡 Tip: This validation is now part of the CI pipeline.');
  console.log('   For faster development, use the quick pre-commit hooks.');
} catch (error) {
  console.error('\n❌ GraphQL validation failed:', error.message);
  process.exit(1);
}
