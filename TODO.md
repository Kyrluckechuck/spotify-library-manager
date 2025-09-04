# Spotify Library Manager - TODO

## ✅ Recently Completed (Current Session)
- [x] **Celery Migration Completed** - Successfully migrated from Huey to Celery with PostgreSQL broker
- [x] **Local Development Fixed** - Updated `dev.py` to use Celery instead of Huey
- [x] **Testing Suite Fixed** - Configured tests to use PostgreSQL with separate test database
- [x] **Django Deprecation Warnings Fixed** - Updated to use STORAGES instead of deprecated settings
- [x] **TanStack Directory Sync Issues Fixed** - Enhanced .gitignore to properly exclude .tanstack/ directories

## High Priority (Immediate)
- [ ] **Fix Makefile dev commands** - Update local development commands to be Docker-compatible
- [ ] **Update CELERY_MIGRATION_SUMMARY.md** - Fix documentation that mentions Redis (should be PostgreSQL)
- [ ] **Update README development section** - Clarify Docker-only approach vs local development

## Backend
- [ ] **Event bus: extract album ID from task args** - Improve task event handling
- [ ] **Async/await cleanup where needed** - Lightweight pass through codebase
- [ ] **API input validation for mutations** - Add incremental validation improvements
- [ ] **Downloader fallback** - Implement `spotdl_wrapper` with settings gate
- [ ] **Fix Django 5.1 deprecation warnings** - Already partially addressed, may need more
- [ ] **Implement downloader fallback (`spotdl_wrapper`)** - Add fallback to yt-dlp when no Spotify AAC

## Frontend
- [ ] **Add `useRequestState` helper** - Wire to routes for better request handling
- [ ] **Implement retries and optimistic updates** - For key mutations
- [ ] **Spotify search feature** - Add search for artists, albums, songs, playlists
- [ ] **Add search UI components** - Frontend components for search functionality

## CI/CD and Operations
- [ ] **Monitor CI on main after merge** - Address any flakes that arise
- [ ] **Add nightly smoke test workflow** - `compose up + /healthz` check
- [ ] **Optimize Docker image size** - Multi-stage builds and cache tuning

## Monitoring and Observability  
- [ ] **Dev: GraphQL query logging** - Simple logging implementation
- [ ] **Prod: basic error tracking hook** - For production environments

## Repository Hygiene and Developer Experience
- [ ] **Unify Node package manager** - Standardize on Yarn, remove package-lock.json
- [ ] **Align Python version requirements** - README vs pyproject.toml consistency (3.11+ vs 3.13+)
- [ ] **Documentation and onboarding improvements**:
  - [ ] Finish migration notes for settings.yaml
  - [ ] Update README onboarding (first run, required env vars, cookie export, device.wvd)
  - [ ] Replace README Docker placeholder with exact commands and expected URLs
- [ ] **Repository templates** - `.github/ISSUE_TEMPLATE` and `PULL_REQUEST_TEMPLATE.md`
- [ ] **Optional: Fix branch name typo** - `overhual-frontend-tanstack` → `overhaul-frontend-tanstack`

## Features and Enhancements
- [ ] **Tracked Playlists improvements** - Improve update experience (not URL-locked)
- [ ] **Configurable periodic task intervals** - Allow customization of sync intervals  
- [ ] **Add artists directly** - Add by artist name (not just URL)
- [ ] **Frontend UX improvements** - Loading skeletons for initial loads (optional)

## Quality of Life
- [ ] **Re-add Downloader configurations loading** - Via settings.yaml
- [ ] **Improve onboarding documentation** - Add critical first startup steps

## Notes
- **Celery + PostgreSQL setup is working perfectly** - No Redis needed
- **Docker-first approach is recommended** - Local development should use containers
- **Test suite uses separate PostgreSQL database** - `test_spotify_library_manager` 
- **TanStack Router files are now properly ignored** - No more sync conflicts
