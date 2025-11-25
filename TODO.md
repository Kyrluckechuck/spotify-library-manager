# Spotify Library Manager - TODO

## High Priority (Immediate)
- [x] **Fix Makefile dev commands** - Update local development commands to be Docker-compatible
- [x] **Update CELERY_MIGRATION_SUMMARY.md** - Fix documentation that mentions Redis (should be PostgreSQL) - Resolved by deleting outdated file
- [x] **Update or create documentation for contributors** - Acknowledge it's a docker-first environment

## Backend
- [x] **Event bus: extract album ID from task args** - Improve task event handling
- [x] **Async/await cleanup where needed** - Lightweight pass through codebase
- [x] **API input validation for mutations** - Add incremental validation improvements
- [x] **Fix Django 5.1 deprecation warnings** - No deprecation warnings found in testing
- [x] **Downloader with yt-dlp fallback** - spotdl_wrapper uses YouTube Music via yt-dlp (already implemented)
- [x] **Task visualization dashboard** - Show scheduled tasks (beat periodic tasks + ad-hoc queued tasks)
- [x] **Add periodic heartbeat updates during long downloads** - Implemented progress callbacks in spotdl_wrapper every 5 songs

## Frontend
- [x] **Add `useRequestState` helper** - Wire to routes for better request handling
- [x] **Spotify search feature** - Add search for artists, albums, songs, playlists
- [x] **Add search UI components** - Frontend components for search functionality

## Frontend (Rejected Ideas - Do Not Implement)
- **Retries for mutations** - Most mutations either succeed or indicate real problems (DB/auth issues). Task operations enqueue jobs, don't need retries.
- **Optimistic updates** - Library management requires accuracy over perceived speed. False states confuse users about tracking/sync status.

## CI/CD and Operations
- [x] **Optimize Docker image size** - Multi-stage builds, static FFmpeg, cache mounts, cleanup

## Repository Hygiene and Developer Experience
- [x] **Unify Node package manager** - Standardized on Yarn, added packageManager field
- [x] **Align Python version requirements** - All components now use Python 3.13+
- [x] **Documentation and onboarding improvements** - README cleaned up, deprecated sections removed
- [x] **Repository templates** - Bug report, feature request, and PR templates added

## Features and Enhancements
- [x] **Artist Detail Page** - Dedicated page showing artist info, albums, and songs
  - [x] Backend: Add `albumCount`, `downloadedAlbumCount`, `songCount` to Artist GraphQL type
  - [x] Frontend: New route `artists_.$artistId.tsx` with single scrollable layout
  - [x] Frontend: New hook `useArtistDetailPage.ts`
  - [x] Frontend: Update `GetArtist` query to include new counts
  - [x] Frontend: Make artist table rows clickable → navigate to detail page
- [ ] **Tracked Playlists improvements** - Improve update experience (not URL-locked)
- [ ] **Configurable periodic task intervals** - Allow customization of sync intervals
- [ ] **Add artists directly** - Add by artist name (not just URL)
- [ ] **Frontend UX improvements** - Loading skeletons for initial loads (optional)

## Notes
- Priority should be given to items affecting active development workflows
- Docker-first development approach is preferred for consistency
