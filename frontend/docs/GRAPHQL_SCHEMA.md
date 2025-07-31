# GraphQL Schema Management

This document outlines the GraphQL schema management system for the Spotify Library Manager frontend.

## Overview

The frontend uses GraphQL to communicate with the backend API. To prevent schema mismatches and ensure type safety, we have implemented a comprehensive validation system.

## Schema Validation

### Automatic Validation

The project includes automatic schema validation that runs:

1. **Before commits** (via pre-commit hook)
2. **Before type generation** (via npm scripts)
3. **Manually** when needed

### Running Validation

```bash
# Validate schema manually
npm run validate-schema

# Generate types with validation
npm run generate-safe

# Generate types without validation (not recommended)
npm run generate
```

### What Gets Validated

The validation script checks for:

1. **Field name mismatches**:
   - `tracked` → `isTracked`
   - `lastSyncedAt` → `lastSynced`
   - `sort_by` → `sortBy`
   - `sort_direction` → `sortDirection`

2. **Non-existent mutations**:
   - `downloadUrl` (removed)
   - `createPlaylist` (removed)
   - `cleanupStuckTasks` (removed)
   - `activeTasks` (removed)

3. **Parameter type mismatches**:
   - Artist ID parameters (String vs Int)
   - Missing required parameters

## Common Issues and Solutions

### Field Name Mismatches

**Problem**: Using old field names that don't match the backend schema.

**Solution**: Update field names to match the backend:

```graphql
# ❌ Wrong
query GetArtist {
  artist {
    tracked
    lastSyncedAt
  }
}

# ✅ Correct
query GetArtist {
  artist {
    isTracked
    lastSynced
  }
}
```

### Parameter Name Mismatches

**Problem**: Using snake_case parameter names instead of camelCase.

**Solution**: Use camelCase parameter names:

```graphql
# ❌ Wrong
query GetArtists($sort_by: String, $sort_direction: String) {
  artists(sort_by: $sort_by, sort_direction: $sort_direction) {
    # ...
  }
}

# ✅ Correct
query GetArtists($sortBy: String, $sortDirection: String) {
  artists(sortBy: $sortBy, sortDirection: $sortDirection) {
    # ...
  }
}
```

### Non-existent Mutations

**Problem**: Using mutations that were removed from the backend.

**Solution**: Remove or replace with existing mutations:

```graphql
# ❌ These mutations don't exist
mutation DownloadUrl($url: String!) {
  downloadUrl(url: $url) { ... }
}

mutation CreatePlaylist($url: String!) {
  createPlaylist(url: $url) { ... }
}

# ✅ Use existing mutations instead
mutation UpdatePlaylist($playlistId: Int!) {
  updatePlaylist(playlistId: $playlistId) { ... }
}
```

## Development Workflow

### Adding New Queries

1. Create the query in the appropriate file
2. Run validation: `npm run validate-schema`
3. Fix any issues found
4. Generate types: `npm run generate-safe`
5. Test the query in your component

### Modifying Existing Queries

1. Update the query
2. Run validation: `npm run validate-schema`
3. Fix any issues found
4. Generate types: `npm run generate-safe`
5. Update components if field names changed

### Backend Schema Changes

When the backend schema changes:

1. Update frontend queries to match
2. Run validation: `npm run validate-schema`
3. Fix all validation errors
4. Generate types: `npm run generate-safe`
5. Update components as needed

## Troubleshooting

### Validation Fails

If schema validation fails:

1. **Check API server**: Make sure the backend is running on port 5000
2. **Check field names**: Ensure all field names match the backend schema
3. **Check parameters**: Verify parameter names and types
4. **Remove non-existent operations**: Remove any queries/mutations that don't exist

### Type Generation Fails

If type generation fails:

1. **Fix validation errors first**: Run `npm run validate-schema`
2. **Check GraphQL syntax**: Ensure all queries are valid GraphQL
3. **Check network connectivity**: Ensure the API server is accessible
4. **Clear cache**: Delete `node_modules/.cache` and try again

### Common Error Messages

- `"Cannot query field X on type Y"`: Field doesn't exist in schema
- `"Unknown argument X on field Y"`: Parameter doesn't exist
- `"Variable X of type Y used in position expecting type Z"`: Type mismatch

## Best Practices

1. **Always validate before committing**: The pre-commit hook will catch issues
2. **Use the safe generation command**: `npm run generate-safe`
3. **Test queries after changes**: Ensure they work with the backend
4. **Keep queries simple**: Avoid complex nested queries when possible
5. **Document changes**: Update this document when schema changes

## Schema Introspection

To inspect the current schema:

```bash
# Using curl
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"query { __schema { types { name } } }"}'

# Using the validation script
npm run validate-schema
```

## File Structure

```
frontend/
├── src/
│   ├── queries/           # GraphQL query files
│   │   ├── artists.graphql
│   │   ├── tasks.ts
│   │   └── download.ts
│   └── types/
│       └── generated/     # Auto-generated TypeScript types
├── scripts/
│   └── validate-schema.js # Schema validation script
└── docs/
    └── GRAPHQL_SCHEMA.md # This file
```

## Contributing

When contributing to GraphQL queries:

1. Follow the existing patterns
2. Use the validation tools
3. Test your changes thoroughly
4. Update documentation if needed
5. Ensure type safety is maintained

## Code Style

### File Endings

All files must end with a newline character. This is enforced by:

- **ESLint rule**: `eol-last: 'error'`
- **Pre-commit hook**: Checks for files without trailing newlines
- **Manual check**: `npm run check-newlines`
- **Auto-fix**: `npm run fix-newlines`

### GraphQL Schema Validation

Before committing:

1. Run `npm run check-newlines` to ensure all files end with newlines
2. Run `npm run validate-schema` to check GraphQL queries
3. Run `npm run generate-safe` to regenerate types safely

The pre-commit hook will automatically run these checks and block commits if issues are found. 
