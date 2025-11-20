# Contributing to Spotify Library Manager

Thank you for your interest in contributing! This project uses a **Docker-first development approach** for consistency across all development environments.

> **💡 Migrating from Previous Version?** See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for upgrading from Huey to Celery system.

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git
- Node.js 20+ and Yarn (for local frontend development only)

### Development Setup

1. **Clone and configure**
   ```bash
   git clone <repository-url>
   cd spotify-library-manager
   cp .env.example .env
   mkdir -p ./config && cp api/settings.yaml.example ./config/settings.yaml
   ```

2. **Setup dependencies** (if doing any local development)
   ```bash
   make setup
   ```

3. **Start the full development stack**
   ```bash
   make dev-container
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - API GraphQL: http://localhost:5000/graphql (internal)

### Required Configuration
- Export Spotify cookies to `./config/youtube_music_cookies.txt`
- Update `./config/settings.yaml` with your preferences
- Ensure `.env` has proper database credentials

## Development Workflow

### Primary Commands

| Command | Purpose |
|---------|---------|
| `make dev-container` | Start full development stack (recommended) |
| `make dev-container-down` | Stop all services |
| `make dev-container-logs` | View logs from all services |
| `make test-docker` | Run tests in containers (recommended) |
| `make lint` | Run linting for API and frontend |
| `make format` | Format and auto-fix code issues |

### Service-Specific Logs
```bash
make dev-container-logs-web      # API server logs
make dev-container-logs-frontend # Frontend dev server logs  
make dev-container-logs-worker   # Celery worker logs
```

### Alternative: Local Development
If you need to run services locally (not recommended for beginners):
```bash
make dev-api      # Start API server locally
make dev-frontend # Start frontend dev server locally
make dev-worker   # Start Celery worker locally
```

## Testing

### Docker Testing (Recommended)
```bash
make test-docker              # Run all tests in containers
make test-api-docker          # API tests only
make test-frontend-docker     # Frontend tests only
```

### Local Testing
```bash
make test                     # Run all tests locally
make test-api                 # API tests with coverage
make test-frontend           # Frontend tests
```

### Test Variants
```bash
make test-api-unit           # Unit tests only
make test-api-integration    # Integration tests only
make test-frontend-coverage  # Frontend with coverage report
```

## Code Quality

### Linting and Formatting
```bash
make lint                    # Check code quality (all)
make lint-api               # Python linting (flake8, mypy, etc.)
make lint-frontend          # TypeScript/React linting
make format                 # Auto-fix formatting issues
```

### Standards
- **Python**: Black formatting, isort imports, mypy type checking, flake8 linting
- **TypeScript**: ESLint with React rules, Prettier formatting
- **Testing**: 80%+ coverage target for critical paths
- **Git**: Conventional commit messages preferred

## Architecture Overview

This is a full-stack application with:

- **Backend**: Django/FastAPI hybrid with GraphQL API (Strawberry)
- **Frontend**: React + TypeScript with TanStack Router
- **Task Queue**: Celery with PostgreSQL broker (no Redis needed)
- **Database**: PostgreSQL with Django migrations
- **Build Tools**: Vite (frontend), Docker Compose (services)

For detailed technical information, see `CLAUDE.md`.

## Docker Services

The development stack includes:
- `web`: FastAPI application server (port 5000, internal)
- `frontend`: Nginx-served React build (port 3000, exposed)
- `worker`: Celery worker for background tasks
- `beat`: Celery beat scheduler
- `postgres`: PostgreSQL database (port 5432, exposed)

## Common Tasks

### Adding GraphQL Operations
1. Define resolver in `api/src/resolvers/`
2. Add to schema in `api/src/schema/`
3. Run `cd frontend && yarn generate` to update frontend types

### Database Changes
1. Modify models in `api/library_manager/models.py`
2. Create migration: `docker compose exec web python manage.py makemigrations`
3. Apply migration: `docker compose exec web python manage.py migrate`

### Adding Background Tasks
1. Create task in appropriate service module with `@shared_task(bind=True)`
2. Queue via `task_name.delay(args)`
3. Monitor via Django admin or task endpoints

## Troubleshooting

### Permission Issues
If you encounter permission errors with `.tanstack` directories:
```bash
sudo rm -rf .tanstack  # Clear any root-owned temp files
```

### Container Issues
```bash
make dev-container-down  # Stop services
docker compose down -v   # Remove volumes if needed
make dev-container       # Restart
```

### Test Database Issues
Tests use a separate PostgreSQL database (`test_spotify_library_manager`) which is created automatically.

## Getting Help

- Check `CLAUDE.md` for detailed technical documentation
- Review existing issues and PRs for similar problems
- Use Docker logs to debug service issues: `make dev-container-logs`

## Contribution Guidelines

1. **Fork and create feature branch**: `git checkout -b feature/your-feature`
2. **Follow code standards**: Run `make lint` and `make format`
3. **Add tests**: Maintain or improve test coverage
4. **Test thoroughly**: Run `make test-docker` before submitting
5. **Document changes**: Update relevant docs if needed
6. **Submit PR**: Include clear description of changes

Thank you for contributing! 🎵
