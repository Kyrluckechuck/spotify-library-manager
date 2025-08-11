# TODO

## GraphQL Schema Management

### Completed ✅
- [x] Fixed GraphQL schema mismatches between frontend and backend
- [x] Updated field names to match schema (`tracked` → `isTracked`, `lastSyncedAt` → `lastSynced`)
- [x] Fixed parameter names (`sortBy`, `sortDirection` instead of `sort_by`, `sort_direction`)
- [x] Removed non-existent mutations (`downloadUrl`, `createPlaylist`, `cleanupStuckTasks`)
- [x] Fixed task history structure (`logMessages` as string array, not object array)
- [x] Regenerated GraphQL types successfully
- [x] Updated frontend components to use correct field names

### Infrastructure Improvements
- [x] **Create automated GraphQL schema validation**
  - [x] Add pre-commit hook to validate schema consistency
  - [x] Create schema introspection script to detect mismatches
  - [x] Set up CI/CD pipeline for schema testing
  - [x] Implement schema versioning and migration tools
- [x] **Create proactive GraphQL issue detection**
  - [x] Enhanced schema validation with async/sync context detection
  - [x] Comprehensive GraphQL operations testing
  - [x] Performance monitoring and error analysis
  - [x] Automated issue reporting with actionable suggestions

### Development Workflow
- [ ] **Add schema validation to development workflow**
  - [ ] Create schema validation script that runs on file changes
  - [ ] Add GraphQL schema testing to yarn scripts
  - [ ] Implement schema debugging tools
  - [ ] Add schema documentation generation

### Testing and Validation
- [x] **Create comprehensive GraphQL schema tests**
  - [x] Test all queries, mutations, and subscriptions
  - [x] Validate type safety across frontend-backend boundary
  - [x] Test error handling and edge cases
  - [x] Test pagination and filtering functionality
  - [x] Created comprehensive test suite for all routes (artists, playlists, albums, songs, tasks)
  - [x] Added GraphQL mocking infrastructure with realistic test data
  - [x] Created GraphQL test runner for backend integration testing
  - [x] Added test scripts to package.json for easy execution

### Documentation
- [ ] **Document GraphQL schema and API**
  - [ ] Document all GraphQL types and their relationships
  - [ ] Create API usage examples
  - [ ] Document error codes and handling
  - [ ] Create troubleshooting guide for schema issues

### Important and should be prioritized
- [x] Remove all useless comments again
- [x] Add newline at end of file rule for repo somehow

### Completed Infrastructure
- [x] **Repo-wide newline enforcement**
  - [x] Created repo-wide pre-commit hook (`.git/hooks/pre-commit`)
  - [x] Added Python script for checking/fixing newlines (`scripts/check-repo-newlines.py`)
  - [x] Added Makefile commands (`make check-newlines`, `make fix-newlines`)
  - [x] Fixed 15 files that were missing trailing newlines
  - [x] Integrated with existing frontend newline checking
  - [x] Added Python linting to pre-commit checks

- [x] **Fixed GraphQL field name mismatches**
  - [x] Updated artists route to use `isTracked` instead of `tracked`
  - [x] Updated ArtistsTable component to use `isTracked` and `lastSynced`
  - [x] Updated test files to use correct field names
  - [x] Regenerated GraphQL types
  - [x] Fixed blank page issues on `/artists` and `/` routes
  - [x] Removed non-existent mutations (`DownloadUrlDocument`, `CreatePlaylistDocument`, `GetActiveTasksDocument`)
  - [x] Updated PlaylistModal to only handle editing (create functionality removed)
  - [x] Fixed TaskHistory log messages structure (now simple array of strings)
  - [x] Removed `/songs` route and components (not in schema)
  - [x] Fixed field name issues (`spotifyUri` → `spotifyGid`)
  - [x] Updated all components to use correct GraphQL types (`Playlist` instead of `TrackedPlaylist`)

### Backend TODOs
- [ ] **Configuration Management**
  - [ ] Make album types configurable (allow "appears_on" to be optional, or others to be deselected)
  - [ ] Move SECRET_KEY to environment variable in auth service
  - [ ] Replace in-memory user storage with proper user storage in auth service

- [ ] **Downloader Integration**
  - [ ] Re-add spotdl integration once all dependencies are resolved
  - [ ] Implement artist tracking from playlist functionality
  - [ ] Implement spotdl wrapper

- [ ] **Error Handling**
  - [ ] Add error message support to history service

- [ ] **Event Bus Improvements**
  - [ ] Extract playlist ID from task args in event bus
  - [ ] Extract album ID from task args in event bus

## Important things
- There are a lot of inline imports in the frontend folder. Should those be replaced with beginning of file imports?
- There are a lot of inline imports in the api folder. Should those be replaced with beginning of file imports?
- I'd also love to add the ability to search for a specific song, artist, or playlist, so essentially spotify search, to the "app". If you're still working on stuff, just add this to the TODO file for now.


## Backend Improvements

### Async/Await Standardization
- [ ] Review all Django ORM operations for async compatibility
- [ ] Standardize sync_to_async usage patterns
- [ ] Add comprehensive error handling for async operations
- [ ] Test performance under load

### API Enhancements
- [ ] Add missing mutations that were removed (if needed)
- [ ] Implement proper error handling for all GraphQL operations
- [ ] Add input validation for all mutations
- [ ] Implement proper pagination for all list queries

## Frontend Improvements

### Component Updates
- [ ] Update all components to use correct field names
- [ ] Add proper error handling for GraphQL operations
- [ ] Implement loading states for all async operations
- [ ] Add optimistic updates for mutations

### User Experience
- [ ] Add proper error messages for GraphQL failures
- [ ] Implement retry logic for failed operations
- [ ] Add offline support for critical operations
- [ ] Improve loading and error states

## Monitoring and Debugging

### Development Tools
- [ ] Add GraphQL query logging in development
- [ ] Create schema introspection tools
- [ ] Add performance monitoring for GraphQL operations
- [ ] Implement query complexity analysis

### Production Monitoring
- [ ] Add GraphQL operation monitoring
- [ ] Implement query performance tracking
- [ ] Add error tracking for GraphQL failures
- [ ] Create alerts for schema mismatches

## Next Priority Tasks

### High Priority - Should be done next
- [ ] **Fix TypeScript errors in test files**
  - [ ] Resolve type issues in `frontend/src/__tests__/routes/artists.test.tsx`
  - [ ] Ensure all test files compile without errors
  - [ ] Add proper TypeScript types for all mock data

- [ ] **Run and validate the new test suite**
  - [ ] Execute `yarn test:run` to run all unit tests
  - [ ] Execute `yarn test:graphql` to test backend integration
  - [ ] Fix any failing tests
  - [ ] Ensure test coverage is comprehensive

- [ ] **Add integration tests for real GraphQL operations**
  - [ ] Test actual backend connectivity
  - [ ] Validate schema consistency between frontend and backend
  - [ ] Test error scenarios with real API responses

### Medium Priority
- [ ] **Add search functionality to the app**
  - [ ] Implement Spotify search for artists, albums, songs, playlists
  - [ ] Add search UI components
  - [ ] Integrate with backend search endpoints

- [ ] **Improve error handling and user feedback**
  - [ ] Add proper error boundaries
  - [ ] Implement retry logic for failed operations
  - [ ] Add loading states and progress indicators

### Low Priority
- [ ] **Performance optimizations**
  - [ ] Implement query result caching
  - [ ] Add optimistic updates for mutations
  - [ ] Optimize bundle size and loading times
