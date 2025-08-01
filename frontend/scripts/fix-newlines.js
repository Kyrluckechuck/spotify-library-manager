#!/usr/bin/env node

/**
 * Fix files that don't end with newlines
 * This script automatically adds newlines to files that need them
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
 * Add newline to a file if it doesn't have one
 */
function addNewlineToFile(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    if (!content.endsWith('\n') && content.length > 0) {
      fs.writeFileSync(filePath, content + '\n', 'utf8');
      return true;
    }
    return false;
  } catch (error) {
    console.error(`Error fixing file ${filePath}:`, error.message);
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
 * Main function to fix all files
 */
function fixNewlines() {
  console.log('🔧 Fixing files without trailing newlines...');

  const projectRoot = path.join(__dirname, '..');
  const files = findFiles(projectRoot);

  const fixedFiles = [];

  for (const file of files) {
    if (!checkFileEndsWithNewline(file)) {
      if (addNewlineToFile(file)) {
        const relativePath = path.relative(projectRoot, file);
        fixedFiles.push(relativePath);
      }
    }
  }

  if (fixedFiles.length === 0) {
    console.log('✅ All files already end with newlines!');
    return;
  }

  console.log(`\n✅ Fixed ${fixedFiles.length} files:`);
  fixedFiles.forEach(file => {
    console.log(`  • ${file}`);
  });
}

// Run if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  fixNewlines();
}

export { fixNewlines };
