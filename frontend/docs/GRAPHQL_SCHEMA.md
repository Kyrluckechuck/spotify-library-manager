# GraphQL Schema Management

## Overview

The frontend uses GraphQL with automatic schema validation to prevent type mismatches.

## Development Commands

```bash
# Validate schema
yarn validate-schema

# Generate types safely
yarn generate-safe

# Generate types (no validation)
yarn generate
```

## Common Issues

### Field Name Mismatches

- `tracked` → `isTracked`
- `lastSyncedAt` → `lastSynced`
- `sort_by` → `sortBy`
- `sort_direction` → `sortDirection`

### Removed Operations

- `downloadUrl` (removed)
- `createPlaylist` (removed)
- `cleanupStuckTasks` (removed)
- `activeTasks` (removed)

## Validation

The pre-commit hook automatically validates:

1. Schema field names match backend
2. Parameter types are correct
3. No non-existent operations are used

## File Structure

```
frontend/
├── src/queries/          # GraphQL query files
├── src/types/generated/  # Auto-generated TypeScript types
└── scripts/validate-schema.js
```
