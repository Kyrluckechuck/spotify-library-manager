
This list removes completed items and internal-only documentation tasks (e.g., public GraphQL API docs). Remaining items are actionable and prioritized.

## High Priority
- [x] Verify dev entrypoint works as intended
  - `make dev` calls `dev.py`, which exists and starts services; no change needed.
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
  - [x] Parameterize music directory via env (e.g., `MUSIC_DIR`) in compose instead of hard-coded path
  - [x] Move Huey SQLite file to `/config/db/huey.sqlite3` to persist across restarts
  - [ ] Review image size; switch to a multi-stage build and leverage dependency caching
  - [x] Add CI workflow to build and push images (GHCR, buildx cache) and run smoke tests (migrate + hit `/healthz`)
  - [x] Replace README Docker TODO with concrete `docker compose up` instructions and a sample `.env.example`
  - [ ] Verify Docker images work on this branch end-to-end (build, migrate, run)

### CI/CD
- [x] Add GitHub Actions workflow(s)
  - [x] API: lint (flake8/black/isort/mypy/pylint), tests (unit + selected integration)
  - [x] Frontend: lint, unit tests
  - [x] GraphQL: run `frontend/scripts/validate-schema.js` and `frontend/scripts/test-graphql-operations.js`
  - [x] Build and push multi-stage images (web, worker) to GHCR with cache
  - [x] Compose up container and run smoke tests (migrate + `/healthz`)

## Backend
- [ ] Configuration management
  - [x] Make album types configurable (allow "appears_on" to be optional, or others deselectable)
  - [x] Move SECRET_KEY to environment variable in auth service
  - [ ] Replace in-memory user storage with persistent storage in auth service

- [ ] Error handling
  - [x] Add error message support to history service

- [ ] Event bus improvements
  - [x] Extract playlist ID from task args in event bus
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
  - [x] Add dedicated health endpoint for container healthchecks

- [ ] Downloader fallback
  - [ ] Implement `api/downloader/spotdl_wrapper.py` and wire fallback to spotdl/yt-dlp when Spotify AAC is unavailable (configurable via `/config/settings.yaml`)

## Frontend
- [ ] Error handling and user feedback
  - [x] Add proper error messages for GraphQL failures
  - [ ] Implement retry logic for failed operations
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

## Repo hygiene and developer experience
- [ ] Unify Node package manager and lockfiles
  - Choose Yarn or npm; remove the other’s lockfile(s). Consolidate to a single lockfile and update Makefile/scripts accordingly.
  - Remove `frontend/package-lock.json` if standardizing on Yarn.
- [ ] Align Python version requirements
  - README mentions Python 3.13+, while `pyproject.toml` targets 3.11+. Decide and align both.
- [ ] Documentation and onboarding
  - Finish migration notes for `settings.yaml` and update README onboarding (first run, required env vars/secrets, cookie export, device.wvd).
  - Replace README Docker placeholder with exact commands and expected URLs.
- [ ] Repository templates and housekeeping
  - Add `.github/ISSUE_TEMPLATE` and `PULL_REQUEST_TEMPLATE.md`
  - Add `.github/workflows/*` for CI/CD (see CI/CD section)
  - Optional: rename branch `overhual-frontend-tanstack` → `overhaul-frontend-tanstack`

## Frontend: Loading & Error State UX Improvements
- [ ] Reusable UI primitives
  - [x] `InlineSpinner` and `PageSpinner`
  - [ ] `SkeletonBlock` and `SkeletonTable` that match table/card layouts
  - [x] `ErrorBanner` with focus management and aria-live
  - [x] `EmptyState` with contextual CTAs
  - [x] `RetryButton` wrapper for re-executing queries
- [ ] Route-level loading
  - [ ] Use TanStack Router pending state to show a top progress bar
- [ ] Query loading patterns
  - [ ] Initial load: render skeletons instead of blank pages
  - [x] Background/refetch: keep previous data; show subtle inline spinner/“Updating…” chip
  - [x] Pagination: show spinner/disable on “Load more”
- [ ] Mutation states
  - [ ] Disable action controls while mutating; inline spinner in buttons
  - [ ] Show inline error near the control; fall back to banner when page-level
- [ ] Error handling UX
  - [ ] Map network vs GraphQL errors to friendly messages
  - [x] Use `ErrorBanner` for blocking failures and keep stale data for non-blocking
  - [ ] Add distinct empty states per view (Artists/Albums/Songs/Playlists/Tasks)
- [ ] Accessibility
  - [x] `aria-busy` on containers, `aria-live='polite'` for status updates, move focus to error banner
- [ ] Global plumbing
  - [ ] Add a small `useRequestState` helper to normalize Apollo `networkStatus` → { isInitial, isRefreshing, isPaginating }
- [ ] Rollout plan
  - [x] Implement primitives and wire into `Artists` as the reference view
  - [x] Apply the pattern to `Albums`, `Songs`, `Playlists`, `Tasks`
