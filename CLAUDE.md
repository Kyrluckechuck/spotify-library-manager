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
- `make validate-types` - Validate GraphQL types (local Node/Yarn required)
- `make lint` - Run linting for both API and frontend (local tools required)
- `make lint-api` - Run comprehensive API linting (local Python required)
- `make lint-frontend` - Run frontend linting using ESLint (local Node/Yarn required)
- `make format` - Format code for both API and frontend (local tools required)

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
- `web`: FastAPI application server (port 5000, internal)
- `frontend`: Nginx-served React production build (port 3000, exposed)
- `worker`: Celery worker for background tasks
- `beat`: Celery beat scheduler for periodic tasks
- `postgres`: PostgreSQL database (port 5432, exposed for testing)

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
1. Define resolver in `api/src/resolvers/`
2. Add to schema in `api/src/schema/`
3. Ensure dev container is running: `make dev-container`
4. Generate types (local Node.js): `cd frontend && GRAPHQL_CODEGEN_ENDPOINT=http://localhost:5000/graphql yarn generate`
5. **Commit the updated types**: `git add frontend/src/types/generated/graphql.ts`
6. Validate types: `make validate-types` (requires local Node.js)
7. Test with `yarn test:graphql` (requires local Node.js)

**Important**: GraphQL types are committed to avoid circular dependency during builds. Always regenerate and commit types after schema changes.

**Environment Variables**:
- `VITE_API_URL`: Runtime GraphQL endpoint (can be relative like `/graphql`)
- `GRAPHQL_CODEGEN_ENDPOINT`: Build-time GraphQL endpoint (must be absolute like `http://localhost:5000/graphql`)

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

## Important Development Patterns

### Task Management
- Background tasks use **Celery with PostgreSQL broker** (no Redis needed)
- Task status tracking via `TaskHistory` model
- Long-running operations (downloads, syncing) are queued
- Use `@shared_task(bind=True)` decorator for async operations
- Task monitoring via Django admin or task status endpoints

### GraphQL Schema
- Auto-generated from Django models using Strawberry
- Type-safe resolvers in `api/src/resolvers/`
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

### Future Automation
- In future you can use the existing cleanup tasks that are used by the CI to perform "easy" fixes for python such as flake8 black and isort, and similarly there are some for yarn/javascript

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
