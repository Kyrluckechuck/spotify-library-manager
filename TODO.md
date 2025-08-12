# TODO

This list removes completed items and internal-only documentation tasks (e.g., public GraphQL API docs). Remaining items are actionable and prioritized.

## High Priority
- [ ] Fix TypeScript errors in test files
  - [ ] Resolve type issues in `frontend/src/__tests__/routes/artists.test.tsx`
  - [ ] Ensure all test files compile without errors
  - [ ] Add proper TypeScript types for all mock data

- [ ] Run and validate the test suite
  - [ ] Execute `yarn test:run` for unit tests
  - [ ] Execute `yarn test:graphql` for backend integration
  - [ ] Fix any failing tests and ensure coverage is adequate

- [ ] Add integration tests for real GraphQL operations
  - [ ] Test actual backend connectivity
  - [ ] Validate schema consistency between frontend and backend
  - [ ] Test error scenarios with real API responses

## Containerization and DevOps
- [ ] Docker images and compose
  - [x] Add non-root user in image and proper file permissions for `/config` and `/mnt/music_spotify`
  - [x] Add healthcheck (simple HTTP or management command) and wire into compose
  - [x] Split dev/prod compose (`docker-compose.override.yml` for dev with bind mounts; prod uses image only)
  - [x] Provide `.env.example` with sane defaults; document required variables
  - [x] Add `docker-compose.override.yml` with local bind mounts for quicker dev
  - [ ] Parameterize music directory via env (e.g., `MUSIC_DIR`) in compose instead of hard-coded path
  - [x] Move Huey SQLite file to `/config/db/huey.sqlite3` to persist across restarts
  - [ ] Review image size; consider multi-stage and dependency caching
  - [ ] Add CI workflow to build/push image (GHCR, buildx cache) and run smoke tests (migrate + hit `/healthz`)

  - [ ] Verify Docker images work on this branch end-to-end (build, migrate, run)

## Backend
- [ ] Configuration management
  - [ ] Make album types configurable (allow "appears_on" to be optional, or others deselectable)
  - [ ] Move SECRET_KEY to environment variable in auth service
  - [ ] Replace in-memory user storage with persistent storage in auth service

- [ ] Downloader integration
  - [ ] Re-add spotdl integration once dependencies are resolved
  - [ ] Implement artist tracking from playlist functionality
  - [ ] Implement spotdl wrapper

- [ ] Error handling
  - [ ] Add error message support to history service

- [ ] Event bus improvements
  - [ ] Extract playlist ID from task args in event bus
  - [ ] Extract album ID from task args in event bus

- [ ] Async/await standardization
  - [ ] Review Django ORM operations for async compatibility
  - [ ] Standardize `sync_to_async` usage patterns
  - [ ] Add comprehensive error handling for async operations
  - [ ] Test performance under load

- [ ] API enhancements
  - [ ] Implement proper error handling for all GraphQL operations
  - [ ] Add input validation for all mutations
  - [ ] Implement proper pagination for all list queries
  - [ ] Re-evaluate previously removed mutations and add back only if needed
  - [ ] Add dedicated health endpoint for container healthchecks

## Frontend
- [ ] Error handling and user feedback
  - [ ] Add proper error messages for GraphQL failures
  - [ ] Implement retry logic for failed operations
  - [ ] Add offline support for critical operations
  - [ ] Improve loading and error states across views

- [ ] Optimistic updates
  - [ ] Add optimistic updates for relevant mutations

## Monitoring and Debugging
- [ ] Development tools
  - [ ] Add GraphQL query logging in development
  - [ ] Create schema introspection tools
  - [ ] Add performance monitoring for GraphQL operations
  - [ ] Implement query complexity analysis

- [ ] Production monitoring
  - [ ] Add GraphQL operation monitoring
  - [ ] Implement query performance tracking
  - [ ] Add error tracking for GraphQL failures
  - [ ] Create alerts for schema mismatches
  - [ ] Add smoke tests that exercise the running container in CI (GraphQL ping, DB migrations)

## Feature: Spotify search
- [ ] Implement Spotify search for artists, albums, songs, playlists
- [ ] Add search UI components
- [ ] Integrate with backend search endpoints

## QOL before merging this branch
  - Add a CI workflow to build/push image and run smoke tests (migrate + hit /healthz)?
  - Ensure any existing CI is updated to make sense with the new build system
