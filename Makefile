.PHONY: build-and-publish dev dev-container dev-container-update dev-container-attach dev-container-down dev-container-logs dev-container-logs-web dev-container-logs-frontend dev-container-logs-worker setup migrate createsuperuser test-migrations clean test test-docker test-api test-api-docker test-frontend test-frontend-docker lint docker-build docker-up docker-down dev-api dev-frontend dev-worker dev-admin dev-db

# Main development command - starts all services
dev:
	python dev.py

# Dev container: run compose with optional local override if present (detached)
dev-container:
	@if [ -f docker-compose.override.yml ]; then \
		docker compose up --build -d; \
	else \
		cp docker-compose.override.example.yml docker-compose.override.yml && echo "Created local override from example"; \
		docker compose up --build -d; \
	fi
	@echo "✅ Containers started in detached mode. Use 'make dev-container-logs' to view logs."

# Dev container update: rebuild and restart app services, keep postgres running for speed
dev-container-update:
	@echo "🔄 Stopping app containers (keeping postgres running)..."
	@docker compose stop web frontend-dev worker beat || true
	@echo "🏗️  Rebuilding and starting app containers..."
	@if [ -f docker-compose.override.yml ]; then \
		docker compose up --build -d web frontend-dev worker beat; \
	else \
		cp docker-compose.override.example.yml docker-compose.override.yml && echo "Created local override from example"; \
		docker compose up --build -d web frontend-dev worker beat; \
	fi
	@echo "🔄 Installing updated requirements in containers..."
	@docker compose exec web pip install -r requirements.txt --quiet || echo "⚠️ Web requirements update failed"
	@docker compose exec worker pip install -r requirements.txt --quiet || echo "⚠️ Worker requirements update failed"
	@docker compose exec beat pip install -r requirements.txt --quiet || echo "⚠️ Beat requirements update failed"
	@echo "✅ App containers updated and running with latest dependencies. Use 'make dev-container-logs' to view logs."

# Attach to the running dev container logs
dev-container-attach:
	docker compose logs -f

dev-container-down:
	docker compose down

dev-container-logs:
	docker compose logs -f

# Tail logs per service
dev-container-logs-web:
	docker compose logs -f web

dev-container-logs-frontend:
	docker compose logs -f frontend

dev-container-logs-worker:
	docker compose logs -f worker

# Individual service development commands
dev-api:
	cd api && python run.py

dev-frontend:
	cd frontend && yarn dev

dev-worker:
	cd api && celery -A celery_app worker --loglevel=info

# Django admin server for accessing Django admin console
dev-admin:
	cd api && python manage.py collectstatic --noinput
	cd api && python manage.py runserver 0.0.0.0:8000

# Access PostgreSQL database
dev-db:
	PGPASSWORD=slm_dev_password psql -h localhost -p 5432 -U slm_user -d spotify_library_manager

# Celery queue management
clear-celery-queue:
	cd api && celery -A celery_app purge -f

# Celery monitoring 
celery-monitor:
	cd api && celery -A celery_app monitor

# Installation and setup
setup:
	# Install API dependencies
	pip install -r requirements.txt
	# Install frontend dependencies
	cd frontend && yarn install

install-api:
	pip install -r requirements.txt

install-frontend:
	cd frontend && yarn install

# Install git hooks from tracked .githooks directory
.PHONY: install-git-hooks
install-git-hooks:
	sh scripts/install-git-hooks.sh

# Database management
migrate:
	cd api && python manage.py migrate

createsuperuser:
	cd api && python manage.py createsuperuser

# Testing
test: test-api test-frontend

# Main API test command with coverage
test-api:
	cd api && python -m pytest tests/ src/tests/ -v -n auto --cov=src --cov=library_manager --cov-report=term-missing

# API test variants
test-api-unit:
	cd api && python -m pytest tests/unit/ src/tests/ -v -n auto -m "not integration"

test-api-integration:
	cd api && python -m pytest tests/integration/ -v -n auto -m integration

# Docker-based testing - runs tests in containerized environment
test-docker: test-api-docker test-frontend-docker

# Main API test command in Docker with coverage
test-api-docker:
	docker compose exec web bash -c "DJANGO_SETTINGS_MODULE=docker_test_settings python -m pytest tests/ src/tests/ -v -n auto --cov=src --cov=library_manager --cov-report=term-missing --reuse-db --nomigrations"

# API test variants in Docker
test-api-unit-docker:
	docker compose exec web bash -c "DJANGO_SETTINGS_MODULE=docker_test_settings python -m pytest tests/unit/ src/tests/ -v -n auto -m 'not integration' --reuse-db --nomigrations"

test-api-integration-docker:
	docker compose exec web bash -c "DJANGO_SETTINGS_MODULE=docker_test_settings python -m pytest tests/integration/ -v -n auto -m integration --reuse-db --nomigrations"


# Frontend testing
test-frontend:
	cd frontend && yarn test:run

test-frontend-watch:
	cd frontend && yarn test

test-frontend-coverage:
	cd frontend && yarn test:coverage

test-frontend-docker:
	@echo "🧪 Running frontend tests in Docker container with volume mounts..."
	docker compose up -d frontend-dev
	docker compose exec frontend-dev yarn test:run

# Frontend test variant that tears down containers after testing
test-frontend-docker-clean:
	@echo "🧪 Running frontend tests in Docker container with volume mounts (will tear down after)..."
	docker compose up -d frontend-dev
	docker compose exec frontend-dev yarn test:run
	docker compose stop frontend-dev
	docker compose rm -f frontend-dev

test-migrations:
	cd api && python manage.py showmigrations

# Linting and Code Quality
lint: lint-api lint-frontend
lint-all: lint format-check
format-check: format-check-api format-check-frontend
format-check-api: format-check-api-black format-check-api-isort
format-check-api-black:
	cd api && python -m black --check --diff .
format-check-api-isort:
	cd api && python -m isort --check-only --diff .
format-check-frontend:
	cd frontend && yarn format:check

lint-api: lint-api-flake8 lint-api-black lint-api-isort lint-api-mypy lint-api-bandit lint-api-pylint

lint-api-flake8:
	cd api && python -m flake8 --extend-ignore=E501,W503 --exclude=.venv,__pycache__,node_modules

lint-api-black:
	cd api && python -m black --check --diff .

lint-api-isort:
	cd api && python -m isort --check-only --diff .

lint-api-mypy:
	cd api && python -m mypy src/ --config-file ../pyproject.toml

lint-api-bandit:
	mkdir -p reports
	cd api && python -m bandit -r src/ library_manager/ -f json -o ../reports/bandit-report.json || true

lint-api-pylint:
	cd api && python -m pylint src/ library_manager/ --rcfile ../pyproject.toml

lint-frontend:
	cd frontend && yarn lint

# Code formatting and auto-fix linting issues
format: fix-lint-api format-frontend

# Auto-fix linting issues (includes formatting)
fix-lint: fix-lint-api fix-lint-frontend

fix-lint-api: fix-lint-api-black fix-lint-api-isort fix-lint-api-flake8

fix-lint-api-black:
	cd api && python -m black . --exclude=.venv,__pycache__,node_modules

fix-lint-api-isort:
	cd api && python -m isort . --profile black

fix-lint-api-flake8:
	cd api && python -c "import re; import pathlib; [open(f, 'w').write(re.sub(r'\[offset : offset', '[offset:offset', open(f).read())) for f in pathlib.Path('.').rglob('*.py') if 'offset : offset' in open(f).read()]"

fix-lint-frontend:
	cd frontend && yarn lint:fix

format-frontend:
	cd frontend && yarn format

# Building
build: build-frontend

build-frontend:
	cd frontend && yarn build

# Docker commands
docker-build:
	@echo "🔨 Building production Docker images..."
	docker build --target backend-prod -t spotify-library-manager:latest .
	docker build --target production -t spotify-library-manager-frontend:latest ./frontend

docker-build-dev:
	@echo "🔨 Building development Docker images..."
	docker build --target backend-dev -t spotify-library-manager:dev .
	docker build --target production -t spotify-library-manager-frontend:dev ./frontend

docker-build-test:
	@echo "🔨 Building test Docker images..."
	docker build --target backend-test -t spotify-library-manager:test .
	docker build --target test -t spotify-library-manager-frontend:test ./frontend

# Use dev-container and dev-container-down instead
docker-up:
	docker compose up -d

docker-down:
	docker compose down

# Build and publish (existing)
build-and-publish:
	sudo podman build -t test_build .
	sudo podman tag test_build ghcr.io/kyrluckechuck/spotify-library-manager:latest
	sudo podman push ghcr.io/kyrluckechuck/spotify-library-manager:latest

# Cleanup
clean:
	rm -rf frontend/node_modules frontend/dist api/__pycache__ api/*.pyc

# Newline checking and fixing
check-newlines:
	python scripts/check-repo-newlines.py check

fix-newlines:
	python scripts/check-repo-newlines.py fix

# Frontend-specific newline commands
check-newlines-frontend:
	cd frontend && yarn check-newlines

fix-newlines-frontend:
	cd frontend && yarn fix-newlines
