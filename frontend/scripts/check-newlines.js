#!/usr/bin/env node

/**
 * Check for files that don't end with newlines
 * This script ensures all files end with a newline character
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// File extensions to check
const EXTENSIONS = [
  '.js',
  '.ts',
  '.tsx',
  '.jsx',
  '.json',
  '.md',
  '.txt',
  '.graphql',
  '.gql',
  '.yml',
  '.yaml',
  '.toml',
  '.ini',
  '.css',
  '.scss',
  '.sass',
  '.html',
  '.xml',
  '.svg',
];

// Directories to ignore
const IGNORE_DIRS = [
  'node_modules',
  'dist',
  'build',
  'coverage',
  '.git',
  '.husky',
  '.vscode',
  '.idea',
  '__pycache__',
  '.pytest_cache',
];

/**
 * Check if a file ends with a newline
 */
function checkFileEndsWithNewline(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return content.endsWith('\n') || content.length === 0;
  } catch (error) {
    console.error(`Error reading file ${filePath}:`, error.message);
    return false;
  }
}

/**
 * Recursively find all files in a directory
 */
function findFiles(dir, files = []) {
  const items = fs.readdirSync(dir);

  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);

    if (stat.isDirectory()) {
      if (!IGNORE_DIRS.includes(item)) {
        findFiles(fullPath, files);
      }
    } else if (stat.isFile()) {
      const ext = path.extname(item);
      if (EXTENSIONS.includes(ext)) {
        files.push(fullPath);
      }
    }
  }

  return files;
}

/**
 * Main function to check all files
 */
function checkNewlines() {
  console.log('🔍 Checking for files without trailing newlines...');

  const projectRoot = path.join(__dirname, '..');
  const files = findFiles(projectRoot);

  const filesWithoutNewlines = [];

  for (const file of files) {
    if (!checkFileEndsWithNewline(file)) {
      filesWithoutNewlines.push(file);
    }
  }

  if (filesWithoutNewlines.length === 0) {
    console.log('✅ All files end with newlines!');
    return;
  }

  console.log('\n❌ Files missing trailing newlines:');
  filesWithoutNewlines.forEach(file => {
    const relativePath = path.relative(projectRoot, file);
    console.log(`  • ${relativePath}`);
  });

  console.log('\n💡 To fix these files, run:');
  console.log('  yarn fix-newlines');

  process.exit(1);
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  checkNewlines();
}

export { checkNewlines };
