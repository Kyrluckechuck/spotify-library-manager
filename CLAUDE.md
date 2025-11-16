# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

**This is a Docker-first application. Use Docker Compose for all development work.**

### Prerequisites
- Docker and Docker Compose
- Node.js 20+ and Yarn (for local frontend development only)
- Git

### Setup
1. `cp .env.example .env` - Configure environment
2. `mkdir -p ./config && cp api/settings.yaml.example ./config/settings.yaml`
3. Export Spotify cookies to `./config/cookies.txt`
4. `make dev-container` - Start full development stack
5. Access:
   - Frontend: http://localhost:3000
   - API: http://localhost:5000/graphql (internal)

## Development Commands

### Primary Development (Docker-based)
- `make dev-container` - **Main development command** - Start full stack (API, Frontend, Worker, Beat, PostgreSQL)
- `make dev-container-down` - Stop all Docker services
- `make dev-container-logs` - Tail logs from all services
- `make dev-container-logs-web` - Tail API server logs only
- `make dev-container-logs-worker` - Tail Celery worker logs only
- `make dev-container-logs-frontend` - Tail frontend dev server logs only

### Alternative Local Development (Advanced)
- `make dev` - Start all services locally (requires local PostgreSQL, Python, Node.js)
- `make dev-api` - Start only the API server locally (requires local Python)
- `make dev-frontend` - Start only the frontend dev server locally (requires local Node.js/Yarn)
- `make dev-worker` - Start only the Celery worker locally (requires local Python)

### Testing & Quality Assurance
- `make test` - Run tests for both API and frontend (local Python/Node required)
- `make test-api` - Run API tests with PostgreSQL test database (local Python required)
- `make test-frontend` - Run frontend tests using Vitest (local Node/Yarn required)
- `make test-api-docker` - Run API tests in Docker container
- `make test-frontend-docker` - Run frontend tests in Docker container

#### Linting Commands
- **`make lint-all`** - **RECOMMENDED: Run ALL linters (API + Frontend) without stopping on first failure** - Shows all issues at once for easier fixing
- **`make lint-api-all`** - **RECOMMENDED: Run ALL API linters without stopping on first failure** - Shows all API issues at once
- `make lint-api` - Run comprehensive API linting (stops on first failure)
- `make lint-frontend` - Run frontend linting using ESLint
- `make format` - Format code for both API and frontend (local tools required)

### GraphQL Type Generation
- **`make graphql-generate`** - **RECOMMENDED: Generate types from local schema** (fast, no server needed)
- `make graphql-schema-fetch` - Fetch schema from running server and regenerate types (use when backend changes)

### Docker Operations
- `make docker-build` - Build Docker image locally
- `docker compose up --build` - Manual Docker startup
- `docker compose down` - Stop Docker services

### Database Management
- `docker compose exec web python manage.py migrate` - Run migrations in web container
- `docker compose exec web python manage.py createsuperuser` - Create superuser in web container
- `make dev-db` - Connect to PostgreSQL database directly

## Architecture Overview

This is a **full-stack Spotify library management application** with the following key components:

### Backend Architecture
- **Django/FastAPI Hybrid**: Django ORM for data models, FastAPI for API serving
- **GraphQL API**: Primary API interface using Strawberry GraphQL framework
- **Celery Task Queue**: PostgreSQL-backed async task processing (no Redis required)
- **Database**: PostgreSQL with Django migrations
- **Configuration**: Dynaconf-based settings loading from `/config/settings.yaml`

### Frontend Architecture
- **React + TypeScript**: Modern React application with strict typing
- **TanStack Router**: File-based routing system
- **Apollo Client**: GraphQL client for API communication
- **Vite**: Build tooling and development server
- **TailwindCSS**: Utility-first CSS framework

### Key Service Structure
- **API Services** (`api/src/services/`): Business logic layer (artist, album, song, playlist management)
- **GraphQL Types** (`api/src/graphql_types/`): Type definitions and schema
- **Django Models** (`api/library_manager/models.py`): Database schema and ORM models
- **Task Management**: Celery workers handle music downloads and library sync operations

### Docker Services

**Production Services** (`docker-compose.yml`):
- `web`: FastAPI application server (port 5000, internal only)
- `frontend`: Nginx serving static React build (port 80 → host:5000, proxies `/graphql` to web service)
- `worker`: Celery worker for background tasks
- `beat`: Celery beat scheduler for periodic tasks
- `postgres`: PostgreSQL database (port 5432)

**Development Services** (`docker-compose.override.yml`):
- `web`: FastAPI with hot-reload (port 5000, internal only)
- `frontend-dev`: Vite dev server with HMR (port 3000, exposed to host)
- `worker`: Celery worker with auto-restart on code changes
- `beat`: Celery beat with auto-restart on code changes
- `postgres`: PostgreSQL database (port 5432, exposed for direct access)

**Port Mapping Rationale**:
- **Development uses port 3000** for Vite dev server (required for HMR/hot module replacement)
- **Production uses port 5000** for nginx (serves static files + proxies API requests)
- API is always internal-only on port 5000, accessed via Docker network or nginx proxy

## Configuration Files

### Required Configuration
- `.env` - Docker environment variables
- `./config/settings.yaml` - Application settings (mounted volume)
- `./config/cookies.txt` - Spotify authentication cookies
- `docker-compose.override.yml` - Local Docker overrides (auto-created)

### Testing Configuration
- Tests use **PostgreSQL** (production parity) with separate `test_spotify_library_manager` database
- Docker tests: Use `make test-api-docker` and `make test-frontend-docker` (no local setup needed)
- Local tests: Use `make test-api` (requires local Python) or `make test-frontend` (requires local Node.js)
- No PYTHONPATH setup needed - pytest handles paths automatically

## Common Development Tasks

### Adding New GraphQL Operations

**Quick Workflow (Recommended - No Running Server Needed!)**:
1. Add mutation/query document to `frontend/src/queries/*.graphql`
2. Generate types locally: `make graphql-generate` or `cd frontend && yarn generate:local`
3. Use the generated types in your components
4. **Commit everything**: `git add frontend/src/types/generated/ frontend/src/queries/`

**When Backend Schema Changes**:
1. Make backend changes in `api/src/schema/` (mutation.py, query.py, or subscription.py)
2. Start dev container: `make dev-container`
3. Fetch updated schema: `make graphql-schema-fetch`
4. **Commit schema and types**: `git add frontend/src/types/generated/`

**How It Works**:
- `schema.graphql` is the source of truth (committed to repo)
- Local type generation uses `schema.graphql` (no server needed)
- Only fetch from server when backend schema changes
- Pre-commit hooks validate GraphQL documents against schema

**Commands**:
- `make graphql-generate` - Generate types from local schema (fast, no server needed)
- `make graphql-schema-fetch` - Fetch schema from running server and regenerate types
- `cd frontend && yarn generate:local` - Same as `make graphql-generate`
- `cd frontend && yarn schema:fetch` - Fetch schema from server (requires GRAPHQL_CODEGEN_ENDPOINT)

**Important**: GraphQL types are committed to avoid circular dependency during builds. The local schema file eliminates the need for a running server during development.

### Database Changes
1. Modify models in `api/library_manager/models.py`
2. Create migration: `docker compose exec web python manage.py makemigrations`
3. Apply migration: `docker compose exec web python manage.py migrate`
4. Update any affected GraphQL types (see GraphQL Operations section)

### Adding Background Tasks
1. Create task function in appropriate service module
2. Decorate with `@celery.task`
3. Queue via `task_name.delay(args)`
4. Monitor via Django admin or task status endpoints

## Code Style & Quality Standards

### Python Standards
- **Black** formatting (88 character line length)
- **isort** for import organization
- **mypy** for type checking with strict settings
- **flake8** for linting
- **bandit** for security analysis
- **pylint** for code quality

### TypeScript/React Standards
- **ESLint** with TypeScript parser
- **Prettier** for consistent formatting
- **Strict TypeScript** configuration
- **React 18** with modern hooks patterns

### Testing Standards
- **pytest** for Python testing with coverage reporting
- **Vitest** for frontend testing
- **Coverage targets**: 80%+ for critical paths

### Linting Workflow

**For Claude Code users:** When fixing linting issues, use `make lint-all` or `make lint-api-all` instead of the standard `make lint-api` command. This runs all linters without stopping on the first failure, allowing you to see and fix all issues at once.

**Standard linting commands** (`make lint-api`, `make lint-frontend`) stop at the first failure, requiring multiple iterations to fix all issues.

**Comprehensive linting commands** (`make lint-all`, `make lint-api-all`) continue through all checks even if some fail, showing you the complete list of issues. This is especially useful when:
- Making changes that affect multiple files
- Fixing linting issues reported by CI/CD
- Reviewing code quality before committing

**What each linter checks:**
- **flake8**: PEP 8 style violations, unused imports, complexity
- **black**: Code formatting (88 char line length)
- **isort**: Import statement ordering
- **mypy**: Type annotations and type safety
- **bandit**: Security vulnerabilities (always passes, generates report)
- **pylint**: Code quality, potential bugs, code smells

## Important Development Patterns

### Task Management
- Background tasks use **Celery with PostgreSQL broker** (no Redis needed)
- Task status tracking via `TaskHistory` model
- Long-running operations (downloads, syncing) are queued
- Use `@shared_task(bind=True)` decorator for async operations
- Task monitoring via Django admin or task status endpoints

#### Periodic Tasks (Celery Beat Schedule)

The following tasks run automatically via Celery Beat (`api/celery_beat_schedule.py`):

| Task | Schedule | Purpose |
|------|----------|---------|
| `sync-all-playlists` | Every 8 hours | Syncs all tracked playlists to detect new songs |
| `retry-failed-playlist-songs` | Weekly (Sunday 3 AM) | Retries downloading songs that failed previously |
| `cleanup-celery-history` | Daily (6 AM) | Removes old task history records (older than 30 days) |
| `cleanup-stale-tasks` | Every 5 minutes | Marks stuck/stale tasks as failed |

**Note**: Celery Beat uses `DatabaseScheduler` which stores schedules in PostgreSQL. To manage schedules:
- **Docker mode**: Use Django shell: `docker compose exec web python manage.py shell`
- **Local mode**: Django Admin at http://localhost:5000/admin/django_celery_beat/
- **Alternative**: Edit schedules directly in `api/celery_beat_schedule.py`

### Async/Sync Boundaries - CRITICAL PATTERN

**IMPORTANT**: This codebase mixes async (FastAPI/Strawberry GraphQL) and sync (Django ORM/Celery) code. You must respect async/sync boundaries.

#### Common Pitfalls and Solutions

1. **Celery Task Calls from Async Context**
   ```python
   # ❌ WRONG - Celery .delay() is sync-only
   async def my_service_method():
       my_task.delay(arg)  # Raises: "You cannot call this from an async context"

   # ✅ CORRECT - Wrap in sync_to_async
   from asgiref.sync import sync_to_async

   async def my_service_method():
       def queue_task():
           my_task.delay(arg)

       await sync_to_async(queue_task)()
   ```

2. **Django ORM from Async Context**
   ```python
   # ❌ WRONG - Django ORM calls are sync
   async def my_service_method():
       album = Album.objects.get(id=1)  # Raises sync_to_async error

   # ✅ CORRECT - Wrap ORM calls
   async def my_service_method():
       album = await sync_to_async(Album.objects.get)(id=1)
       # Or for complex operations:
       def get_album():
           return Album.objects.get(id=1)
       album = await sync_to_async(get_album)()
   ```

3. **Model Methods from Async Context**
   ```python
   # ❌ WRONG - Model save() is sync
   async def my_service_method():
       album.wanted = True
       album.save()  # Raises sync_to_async error

   # ✅ CORRECT - Wrap model methods
   async def my_service_method():
       album.wanted = True
       await sync_to_async(album.save)()
   ```

4. **Lazy-Loading Related Objects**
   ```python
   # ❌ WRONG - Accessing related objects can trigger lazy DB queries
   async def my_service_method():
       album = await sync_to_async(Album.objects.get)(id=1)
       return convert_to_type(album)  # album.artist.name triggers lazy load!

   # ✅ CORRECT - Wrap conversion that accesses relations
   async def my_service_method():
       album = await sync_to_async(Album.objects.get)(id=1)
       return await sync_to_async(convert_to_type)(album)

   # ✅ BETTER - Use select_related to prefetch
   async def my_service_method():
       album = await sync_to_async(
           lambda: Album.objects.select_related("artist").get(id=1)
       )()
       return await sync_to_async(convert_to_type)(album)
   ```

#### When to Use sync_to_async

Use `sync_to_async` whenever calling from async context (GraphQL resolvers, async services):
- **Celery task queuing**: `.delay()` or `.apply_async()`
- **Django ORM queries**: `Model.objects.get()`, `.filter()`, `.create()`, etc.
- **Model methods**: `.save()`, `.delete()`, custom model methods
- **Django transactions**: `transaction.atomic()`
- **Any synchronous library calls**

#### Reference Implementations
See `api/src/services/album.py` for examples:
- `AlbumService.download_album()` - Celery task queuing from async using `sync_to_async`
- `AlbumService.get_by_id()` - ORM queries from async context
- `AlbumService.set_wanted()` - Model save operations from async
- `AlbumService._to_graphql_type()` - Converting Django models with lazy-loading protection

### GraphQL Schema
- Auto-generated from Django models using Strawberry
- Type-safe resolvers in `api/src/schema/` (mutation.py, query.py, subscription.py)
- Frontend types generated via GraphQL Code Generator

### Configuration Management
- Settings cascade: `/config/settings.yaml` → environment variables → defaults
- Use `dynaconf` for dynamic configuration loading
- Database credentials and secrets via environment variables
- STORAGES configuration (not deprecated DEFAULT_FILE_STORAGE)

### Database Operations
- Use Django ORM exclusively for database access
- Database IDs preferred over GIDs for internal operations
- Migrations: `docker compose exec web python manage.py migrate`
- PostgreSQL-specific features used in production
- Tests use separate PostgreSQL database for production parity

## Development Environment Notes

### Docker vs Local Development
- **Recommended**: Use Docker containers for all development (`make dev-container`)
- **Local tools needed**: Node.js/Yarn for frontend type generation and testing
- **Database operations**: Always use `docker compose exec web` for Django management commands
- **Code quality**: Linting/formatting requires local Python and Node.js tools

### Key Container Commands
- `docker compose exec web python manage.py <command>` - Run Django commands in web container
- `docker compose exec web bash` - Shell into web container
- `docker compose logs -f <service>` - View logs for specific service

### Code Quality & Linting
- **Local linting is available and preferred** - Run linting locally instead of in containers when possible:
  - Python (from `/api` directory): `python3 -m flake8 <file>`, `python3 -m black <file>`, `python3 -m isort <file>`
  - Frontend: Use `yarn lint`, `yarn format`, etc. from `/frontend` directory
- Container-based linting is also available but local is faster and more reliable
- In future you can use the existing cleanup tasks that are used by the CI to perform "easy" fixes for python such as flake8 black and isort, and similarly there are some for yarn/javascript

## Frontend React Patterns

### Function Props in Effects - Use Ref Pattern
When a component receives a function prop that will be called inside a `useEffect`, ALWAYS use the ref pattern to avoid requiring the parent to memoize. This makes components robust and defensive.

**Reference implementations**:
- `frontend/src/hooks/useDebouncedSearch.ts` (lines 11-32)
- `frontend/src/components/ui/SearchInput.tsx` (lines 20-35)

**Pattern**: Store function in ref, update ref in separate effect, main effect uses `ref.current` and does NOT include the function in dependencies.

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
- Local testing needs to test port 3000, always
- Do not kill my servers -- I leave them running on purpose. Only restart/update them when the changes actually require it, and don't shut them down when you're done unless I ask. If you have a good reason to do it, you can ask first.
