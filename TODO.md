
This list removes completed items and internal-only documentation tasks (e.g., public GraphQL API docs). Remaining items are actionable and prioritized.

## High Priority (post-merge)
- [ ] Verify Docker images end-to-end (build, migrate, run) on main
- [ ] Optimize Docker image size (multi-stage/cache tuning)
- [ ] Implement downloader fallback (`spotdl_wrapper`) and settings gate

## CI/CD and Ops
- [ ] Monitor CI on main after merge; address flakes
- [ ] Add nightly smoke test workflow (compose up + `/healthz`)

## Backend
- [ ] Event bus: extract album ID from task args
- [ ] Async/await cleanup where needed (lightweight pass)
- [ ] API input validation for mutations (incremental)
- [ ] Downloader fallback (`spotdl_wrapper` with settings)
- [ ] Fix Django 5.1 deprecation warnings
  - [ ] Replace `DEFAULT_FILE_STORAGE` with `STORAGES` setting
  - [ ] Replace `STATICFILES_STORAGE` with `STORAGES` setting

## Frontend
- [ ] Add `useRequestState` helper and wire to routes
- [ ] Implement retries and optimistic updates for key mutations

## Monitoring
- [ ] Dev: GraphQL query logging (simple)
- [ ] Prod: basic error tracking hook (later)

## Feature: Spotify search
- [ ] Implement Spotify search for artists, albums, songs, playlists
- [ ] Add search UI components
- [ ] Integrate with backend search endpoints

## QOL
- [ ] Align Python version in README with `pyproject.toml` (3.11+)

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

## Frontend UX
- [ ] Skeletons for initial loads (optional)
