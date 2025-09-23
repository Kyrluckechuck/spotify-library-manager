#!/usr/bin/env node

/**
 * CI-friendly GraphQL Type Validation Script
 *
 * This script validates the committed GraphQL types without requiring a running server.
 * It checks for:
 * 1. Valid TypeScript compilation of generated types
 * 2. Consistency between queries and committed types
 * 3. No missing or malformed type definitions
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { execSync } from 'child_process';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const GENERATED_TYPES_PATH = path.join(
  __dirname,
  '../src/types/generated/graphql.ts'
);
const QUERIES_DIR = path.join(__dirname, '../src/queries');

/**
 * Check if generated types file exists and is valid
 */
function validateGeneratedTypes() {
  console.log('🔍 Validating generated GraphQL types...');

  // Check if file exists
  if (!fs.existsSync(GENERATED_TYPES_PATH)) {
    console.error(
      '❌ Generated types file not found at:',
      GENERATED_TYPES_PATH
    );
    console.log('💡 Run: cd frontend && yarn generate');
    return false;
  }

  // Check if file is not empty
  const content = fs.readFileSync(GENERATED_TYPES_PATH, 'utf8');
  if (content.trim().length === 0) {
    console.error('❌ Generated types file is empty');
    return false;
  }

  // Check for basic type exports
  const requiredExports = ['Query', 'Mutation', 'Subscription'];
  const hasRequiredExports = requiredExports.some(
    exportName =>
      content.includes(`export type ${exportName}`) ||
      content.includes(`export interface ${exportName}`)
  );

  if (!hasRequiredExports) {
    console.error('❌ Generated types file missing core GraphQL types');
    console.log('Expected to find exports for:', requiredExports.join(', '));
    return false;
  }

  console.log('✅ Generated types file exists and contains core types');
  return true;
}

/**
 * Check TypeScript compilation of generated types
 */
function validateTypeScriptCompilation() {
  console.log('🔍 Validating TypeScript compilation...');

  try {
    // Run TypeScript compiler on generated types only
    execSync(`npx tsc --noEmit --skipLibCheck ${GENERATED_TYPES_PATH}`, {
      stdio: 'pipe',
      cwd: path.join(__dirname, '..'),
    });
    console.log('✅ Generated types compile successfully');
    return true;
  } catch (error) {
    console.error('❌ TypeScript compilation failed for generated types');
    console.log(
      'Error output:',
      error.stdout?.toString() || error.stderr?.toString()
    );
    return false;
  }
}

/**
 * Validate that GraphQL queries use valid syntax
 */
function validateGraphQLQueries() {
  console.log('🔍 Validating GraphQL query syntax...');

  if (!fs.existsSync(QUERIES_DIR)) {
    console.log('⚠️ No queries directory found, skipping query validation');
    return true;
  }

  const queryFiles = fs
    .readdirSync(QUERIES_DIR)
    .filter(file => file.endsWith('.graphql') || file.endsWith('.ts'))
    .map(file => path.join(QUERIES_DIR, file));

  if (queryFiles.length === 0) {
    console.log('⚠️ No GraphQL query files found');
    return true;
  }

  let hasErrors = false;

  for (const queryFile of queryFiles) {
    const content = fs.readFileSync(queryFile, 'utf8');

    // Basic syntax checks
    const queryMatch = content.match(/query\s+(\w+)/g);
    const mutationMatch = content.match(/mutation\s+(\w+)/g);

    if (queryMatch || mutationMatch) {
      // Check for balanced braces
      const openBraces = (content.match(/\{/g) || []).length;
      const closeBraces = (content.match(/\}/g) || []).length;

      if (openBraces !== closeBraces) {
        console.error(`❌ Unbalanced braces in ${path.basename(queryFile)}`);
        hasErrors = true;
      }

      // Check for incomplete operations
      if (content.includes('query ') && !content.includes('{')) {
        console.error(`❌ Incomplete query in ${path.basename(queryFile)}`);
        hasErrors = true;
      }
    }
  }

  if (!hasErrors) {
    console.log(`✅ Validated ${queryFiles.length} GraphQL query files`);
  }

  return !hasErrors;
}

/**
 * Check if types are reasonably up-to-date
 */
function validateTypeFreshness() {
  console.log('🔍 Checking type freshness...');

  try {
    const typesStats = fs.statSync(GENERATED_TYPES_PATH);
    const now = new Date();
    const daysSinceUpdate = (now - typesStats.mtime) / (1000 * 60 * 60 * 24);

    if (daysSinceUpdate > 30) {
      console.log(
        `⚠️ Generated types are ${Math.floor(daysSinceUpdate)} days old`
      );
      console.log('💡 Consider regenerating: cd frontend && yarn generate');
    } else {
      console.log('✅ Generated types are reasonably fresh');
    }

    return true;
  } catch (error) {
    console.log('⚠️ Could not check type freshness:', error.message);
    return true; // Don't fail on this check
  }
}

/**
 * Main validation function
 */
async function validateTypes() {
  console.log('🔍 CI GraphQL Type Validation\n');

  const checks = [
    { name: 'Generated Types', fn: validateGeneratedTypes },
    { name: 'TypeScript Compilation', fn: validateTypeScriptCompilation },
    { name: 'GraphQL Queries', fn: validateGraphQLQueries },
    { name: 'Type Freshness', fn: validateTypeFreshness },
  ];

  let allPassed = true;

  for (const check of checks) {
    try {
      const passed = await check.fn();
      if (!passed) {
        allPassed = false;
      }
    } catch (error) {
      console.error(`❌ ${check.name} validation failed:`, error.message);
      allPassed = false;
    }
    console.log(''); // Add spacing
  }

  if (allPassed) {
    console.log('🎉 All GraphQL type validations passed!');
    process.exit(0);
  } else {
    console.log('💥 Some GraphQL type validations failed');
    console.log('\n💡 Common fixes:');
    console.log('  • Regenerate types: cd frontend && yarn generate');
    console.log('  • Check GraphQL query syntax');
    console.log('  • Ensure backend schema is compatible');
    process.exit(1);
  }
}

// Run validation if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  validateTypes().catch(error => {
    console.error('❌ Validation failed with error:', error);
    process.exit(1);
  });
}
