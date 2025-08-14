# Changelog

## [1.0.0] - 2025-08-13

- Frontend overhaul using TanStack Router + Apollo
- Added CI with backend/frontend lint/tests, Docker smoke + GraphQL validation
- Docker images published to GHCR; compose healthchecks wired
- Bridged legacy Django migration history to new app layout (see README upgrade notes)
- Yarn-only frontend with single lockfile; cleaned lockfile duplication
- Docs: Docker quickstart and .env.example
