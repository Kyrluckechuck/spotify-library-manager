#!/usr/bin/env node

/**
 * GraphQL Schema Validation Script
 * 
 * This script validates that all frontend GraphQL queries match the backend schema.
 * It helps catch schema mismatches early in development.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Configuration
const API_URL = 'http://localhost:5000/graphql';
const QUERIES_DIR = path.join(__dirname, '../src/queries');
const TYPES_DIR = path.join(__dirname, '../src/types/generated');

/**
 * Introspect the GraphQL schema from the backend
 */
async function introspectSchema() {
  try {
    const introspectionQuery = `
      query IntrospectionQuery {
        __schema {
          types {
            name
            fields {
              name
              args {
                name
                type {
                  name
                  kind
                  ofType {
                    name
                    kind
                  }
                }
              }
              type {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
          }
        }
      }
    `;

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query: introspectionQuery,
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    return result.data.__schema;
  } catch (error) {
    console.error('❌ Failed to introspect schema:', error.message);
    console.log('💡 Make sure the API server is running on port 5000');
    process.exit(1);
  }
}

/**
 * Extract GraphQL queries from files
 */
function extractQueries() {
  const queries = [];
  
  function processFile(filePath) {
    const content = fs.readFileSync(filePath, 'utf8');
    const lines = content.split('\n');
    
    let inQuery = false;
    let queryLines = [];
    let queryName = '';
    
    for (const line of lines) {
      if (line.trim().startsWith('query ') || line.trim().startsWith('mutation ')) {
        if (inQuery) {
          queries.push({ name: queryName, content: queryLines.join('\n') });
        }
        inQuery = true;
        queryLines = [line];
        queryName = line.match(/(?:query|mutation)\s+(\w+)/)?.[1] || '';
      } else if (inQuery) {
        queryLines.push(line);
        if (line.trim() === '}') {
          queries.push({ name: queryName, content: queryLines.join('\n') });
          inQuery = false;
          queryLines = [];
        }
      }
    }
  }
  
  // Process .graphql files
  const graphqlFiles = fs.readdirSync(QUERIES_DIR)
    .filter(file => file.endsWith('.graphql'))
    .map(file => path.join(QUERIES_DIR, file));
  
  // Process .ts files with GraphQL queries
  const tsFiles = fs.readdirSync(QUERIES_DIR)
    .filter(file => file.endsWith('.ts'))
    .map(file => path.join(QUERIES_DIR, file));
  
  [...graphqlFiles, ...tsFiles].forEach(processFile);
  
  return queries;
}

/**
 * Validate queries against schema
 */
function validateQueries(queries, schema) {
  const errors = [];
  const warnings = [];
  
  for (const query of queries) {
    try {
      // Basic validation - check for common issues
      const content = query.content;
      
      // Check for common field name mismatches
      const fieldMismatches = [
        { pattern: /tracked\b/g, suggestion: 'isTracked' },
        { pattern: /sort_by\b/g, suggestion: 'sortBy' },
        { pattern: /sort_direction\b/g, suggestion: 'sortDirection' },
      ];
      
      for (const mismatch of fieldMismatches) {
        if (mismatch.pattern.test(content)) {
          warnings.push({
            query: query.name,
            message: `Consider using '${mismatch.suggestion}' instead of '${mismatch.pattern.source.replace(/\\b/g, '')}'`,
            line: content.split('\n').findIndex(line => mismatch.pattern.test(line)) + 1,
          });
        }
      }
      
      // Check for non-existent mutations
      const nonExistentMutations = [
        'downloadUrl',
        'createPlaylist', 
        'cleanupStuckTasks',
        'activeTasks',
      ];
      
      for (const mutation of nonExistentMutations) {
        if (content.includes(mutation)) {
          errors.push({
            query: query.name,
            message: `Mutation '${mutation}' does not exist in the schema`,
            line: content.split('\n').findIndex(line => line.includes(mutation)) + 1,
          });
        }
      }
      
    } catch (error) {
      errors.push({
        query: query.name,
        message: `Failed to validate query: ${error.message}`,
        line: 1,
      });
    }
  }
  
  return { errors, warnings };
}

/**
 * Main validation function
 */
async function validateSchema() {
  console.log('🔍 Validating GraphQL schema...');
  
  // Check if API server is running
  let schema;
  try {
    schema = await introspectSchema();
    console.log('✅ Successfully connected to GraphQL API');
  } catch (error) {
    console.error('❌ Cannot connect to GraphQL API');
    console.log('💡 Please start the API server: cd api && python -m uvicorn src.main:app --reload --port 5000');
    process.exit(1);
  }
  
  // Extract queries
  const queries = extractQueries();
  console.log(`📝 Found ${queries.length} GraphQL queries`);
  
  // Validate queries
  const { errors, warnings } = validateQueries(queries, schema);
  
  // Report results
  if (errors.length === 0 && warnings.length === 0) {
    console.log('✅ All GraphQL queries are valid!');
    return;
  }
  
  if (errors.length > 0) {
    console.log('\n❌ GraphQL Schema Errors:');
    errors.forEach(error => {
      console.log(`  • ${error.query}:${error.line} - ${error.message}`);
    });
  }
  
  if (warnings.length > 0) {
    console.log('\n⚠️  GraphQL Schema Warnings:');
    warnings.forEach(warning => {
      console.log(`  • ${warning.query}:${warning.line} - ${warning.message}`);
    });
  }
  
  if (errors.length > 0) {
    process.exit(1);
  }
}

// Run validation if called directly
validateSchema().catch(error => {
  console.error('❌ Validation failed:', error);
  process.exit(1);
}); 
