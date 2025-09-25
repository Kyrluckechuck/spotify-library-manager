# Spotify Library Manager - TODO

## High Priority (Immediate)
- [x] **Fix Makefile dev commands** - Update local development commands to be Docker-compatible
- [x] **Update CELERY_MIGRATION_SUMMARY.md** - Fix documentation that mentions Redis (should be PostgreSQL) - Resolved by deleting outdated file
- [x] **Update or create documentation for contributors** - Acknowledge it's a docker-first environment

## Backend
- [x] **Event bus: extract album ID from task args** - Improve task event handling
- [x] **Async/await cleanup where needed** - Lightweight pass through codebase
- [x] **API input validation for mutations** - Add incremental validation improvements
- [ ] **Downloader fallback** - Implement `spotdl_wrapper` with settings gate
- [x] **Fix Django 5.1 deprecation warnings** - No deprecation warnings found in testing
- [ ] **Implement downloader fallback (`spotdl_wrapper`)** - Add fallback to yt-dlp when no Spotify AAC
- [ ] **Task visualization dashboard** - Show scheduled tasks (beat periodic tasks + ad-hoc queued tasks)

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
- [x] **Align Python version requirements** - All components now use Python 3.13+
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
- Priority should be given to items affecting active development workflows
- Docker-first development approach is preferred for consistency
