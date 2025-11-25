.PHONY: build-and-publish dev dev-container dev-container-branch dev-container-update dev-container-attach dev-container-down dev-container-logs dev-container-logs-web dev-container-logs-frontend dev-container-logs-worker setup migrate createsuperuser test-migrations clean test test-docker test-api test-api-docker test-frontend test-frontend-docker lint lint-all lint-api lint-frontend docker-build docker-up docker-down dev-api dev-frontend dev-worker dev-admin dev-db docker-cleanup docker-cleanup-full docker-status

# Main development command - starts all services
dev:
	python dev.py

# Auto-detect branch and set BACKEND_IMAGE_TAG for branch-specific images
# Usage: make dev-container-branch (tries current branch, falls back to latest)
dev-container-branch:
	@BRANCH=$$(git branch --show-current | sed 's/\//-/g'); \
	echo "🔍 Detected branch: $$BRANCH"; \
	if docker manifest inspect ghcr.io/kyrluckechuck/spotify-library-manager:$$BRANCH > /dev/null 2>&1; then \
		echo "✅ Found image for branch '$$BRANCH' on GHCR"; \
		BACKEND_IMAGE_TAG=$$BRANCH docker compose up -d; \
	else \
		echo "⚠️  No image found for branch '$$BRANCH', using 'latest'"; \
		docker compose up -d; \
	fi
	@echo "✅ Containers started. Use 'make dev-container-logs' to view logs."

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
	@docker compose exec web pip install -r /requirements/requirements.txt -r /requirements/requirements-dev.txt --quiet || echo "⚠️ Web requirements update failed"
	@docker compose exec worker pip install -r /requirements/requirements.txt -r /requirements/requirements-dev.txt --quiet || echo "⚠️ Worker requirements update failed"
	@docker compose exec beat pip install -r /requirements/requirements.txt -r /requirements/requirements-dev.txt --quiet || echo "⚠️ Beat requirements update failed"
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
# Runs all tests in parallel with 2 workers
test-api:
	cd api && python -m pytest tests/ src/tests/ -v -n 2 --cov=src --cov=library_manager --cov-report=term-missing

# API test variants (for running subsets individually)
test-api-unit:
	cd api && python -m pytest tests/unit/ src/tests/ -v -n 2 --cov=src --cov=library_manager --cov-report=term-missing -m "not integration"

test-api-integration:
	cd api && python -m pytest tests/integration/ -v -n 2 --cov=src --cov=library_manager --cov-report=term-missing -m integration

# Test specific file or folder
# Usage: make test-api-path PATH=tests/unit/test_gid_validation.py
test-api-path:
	@if [ -z "$(PATH)" ]; then \
		echo "❌ Error: PATH variable required"; \
		echo "Usage: make test-api-path PATH=tests/unit/test_gid_validation.py"; \
		exit 1; \
	fi
	cd api && python -m pytest $(PATH) -v -s

# Docker-based testing - runs tests in containerized environment
test-docker: test-api-docker test-frontend-docker

# Main API test command in Docker with coverage
# Runs all tests in parallel with 2 workers
test-api-docker:
	docker compose exec web bash -c "DJANGO_SETTINGS_MODULE=docker_test_settings python -m pytest tests/ src/tests/ -v -n 2 --cov=src --cov=library_manager --cov-report=term-missing --reuse-db"

# API test variants in Docker (for running subsets individually)
test-api-unit-docker:
	docker compose exec web bash -c "DJANGO_SETTINGS_MODULE=docker_test_settings python -m pytest tests/unit/ src/tests/ -v -n 2 --cov=src --cov=library_manager --cov-report=term-missing -m 'not integration' --reuse-db"

test-api-integration-docker:
	docker compose exec web bash -c "DJANGO_SETTINGS_MODULE=docker_test_settings python -m pytest tests/integration/ -v -n 2 --cov=src --cov=library_manager --cov-report=term-missing -m integration --reuse-db"


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

# GraphQL Schema & Type Generation
.PHONY: graphql-generate graphql-generate-local graphql-schema-fetch

graphql-generate-local:
	@echo "📝 Generating GraphQL types from local schema file (no server needed)..."
	@cd frontend && yarn generate:local
	@echo "✅ GraphQL types generated from local schema!"

graphql-schema-fetch:
	@echo "🔄 Fetching GraphQL schema from running server..."
	@if docker compose ps web | grep -q "Up"; then \
		docker compose exec frontend-dev sh -c "GRAPHQL_CODEGEN_ENDPOINT=http://web:5000/graphql yarn schema:fetch"; \
		echo "✅ Schema fetched and types generated!"; \
	else \
		echo "❌ Error: Web service is not running. Start it with 'make dev-container' first."; \
		exit 1; \
	fi

graphql-generate: graphql-generate-local

# Linting and Code Quality
lint: lint-api lint-frontend
format-check: format-check-api format-check-frontend
format-check-api: format-check-api-black format-check-api-isort
format-check-api-black:
	cd api && python -m black --check --diff .
format-check-api-isort:
	cd api && python -m isort --check-only --diff .
format-check-frontend:
	cd frontend && yarn format:check

# Run all API linting in parallel - shows results as each completes
lint-api:
	@mkdir -p .lint-tmp; \
	rm -f .lint-tmp/*; \
	echo "=== Running all API linters in parallel ==="; \
	echo ""; \
	(cd api && python -m flake8 --extend-ignore=E501,W503 --exclude=.venv,__pycache__,node_modules) > .lint-tmp/flake8.log 2>&1 & \
	PID_FLAKE8=$$!; \
	(cd api && python -m black --check --diff .) > .lint-tmp/black.log 2>&1 & \
	PID_BLACK=$$!; \
	(cd api && python -m isort --check-only --diff .) > .lint-tmp/isort.log 2>&1 & \
	PID_ISORT=$$!; \
	(cd api && python -m mypy src/ --config-file ../pyproject.toml) > .lint-tmp/mypy.log 2>&1 & \
	PID_MYPY=$$!; \
	(mkdir -p reports && cd api && python -m bandit -r src/ library_manager/ -f json -o ../reports/bandit-report.json) > .lint-tmp/bandit.log 2>&1 & \
	PID_BANDIT=$$!; \
	(cd api && python -m pylint src/ library_manager/ --rcfile ../pyproject.toml) > .lint-tmp/pylint.log 2>&1 & \
	PID_PYLINT=$$!; \
	printf "$$PID_FLAKE8:flake8:0\n$$PID_BLACK:black:0\n$$PID_ISORT:isort:0\n$$PID_MYPY:mypy:0\n$$PID_BANDIT:bandit:1\n$$PID_PYLINT:pylint:0\n" > .lint-tmp/pids; \
	TOTAL=6; COMPLETED=0; FAIL=0; SPIN=0; \
	printf "\033[?25l"; \
	while [ $$COMPLETED -lt $$TOTAL ]; do \
		SPIN=$$(($$SPIN + 1)); \
		case $$(($$SPIN % 10)) in \
			0) CHAR="⠋" ;; 1) CHAR="⠙" ;; 2) CHAR="⠹" ;; 3) CHAR="⠸" ;; 4) CHAR="⠼" ;; \
			5) CHAR="⠴" ;; 6) CHAR="⠦" ;; 7) CHAR="⠧" ;; 8) CHAR="⠇" ;; 9) CHAR="⠏" ;; \
		esac; \
		printf "\r🚀 Running: "; \
		grep -v "^DONE:" .lint-tmp/pids > .lint-tmp/pids.active 2>/dev/null || touch .lint-tmp/pids.active; \
		while IFS=: read -r PID NAME IGNORE_FAIL || [ -n "$$PID" ]; do \
			[ -z "$$PID" ] && continue; \
			if ! kill -0 $$PID 2>/dev/null; then \
				wait $$PID; EXIT_CODE=$$?; \
				printf "\r\033[K"; \
				echo "--- $$NAME (done) ---"; \
				cat .lint-tmp/$$NAME.log; \
				echo ""; \
				if [ "$$IGNORE_FAIL" != "1" ] && [ $$EXIT_CODE -ne 0 ]; then \
					FAIL=$$(($$FAIL + 1)); \
				fi; \
				sed -i "s/^$$PID:$$NAME:$$IGNORE_FAIL$$/DONE:$$PID:$$NAME:$$IGNORE_FAIL/" .lint-tmp/pids; \
				COMPLETED=$$(($$COMPLETED + 1)); \
			else \
				printf "%s" "$$CHAR $$NAME  "; \
			fi; \
		done < .lint-tmp/pids.active; \
		sleep 0.1; \
	done; \
	printf "\r\033[K"; \
	printf "\033[?25h"; \
	rm -rf .lint-tmp; \
	echo "=== Linting complete: $$FAIL check(s) failed ==="; \
	exit $$FAIL

# Individual linter targets (for running specific linters manually)

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

# Run all linting (API + Frontend) in parallel - shows results as each completes
lint-all:
	@mkdir -p .lint-tmp; \
	rm -f .lint-tmp/*; \
	echo "=== Running all linters (API + Frontend) in parallel ==="; \
	echo ""; \
	(cd api && python -m flake8 --extend-ignore=E501,W503 --exclude=.venv,__pycache__,node_modules) > .lint-tmp/flake8.log 2>&1 & \
	PID_FLAKE8=$$!; \
	(cd api && python -m black --check --diff .) > .lint-tmp/black.log 2>&1 & \
	PID_BLACK=$$!; \
	(cd api && python -m isort --check-only --diff .) > .lint-tmp/isort.log 2>&1 & \
	PID_ISORT=$$!; \
	(cd api && python -m mypy src/ --config-file ../pyproject.toml) > .lint-tmp/mypy.log 2>&1 & \
	PID_MYPY=$$!; \
	(mkdir -p reports && cd api && python -m bandit -r src/ library_manager/ -f json -o ../reports/bandit-report.json) > .lint-tmp/bandit.log 2>&1 & \
	PID_BANDIT=$$!; \
	(cd api && python -m pylint src/ library_manager/ --rcfile ../pyproject.toml) > .lint-tmp/pylint.log 2>&1 & \
	PID_PYLINT=$$!; \
	(cd frontend && yarn lint) > .lint-tmp/frontend.log 2>&1 & \
	PID_FRONTEND=$$!; \
	printf "$$PID_FLAKE8:flake8:0\n$$PID_BLACK:black:0\n$$PID_ISORT:isort:0\n$$PID_MYPY:mypy:0\n$$PID_BANDIT:bandit:1\n$$PID_PYLINT:pylint:0\n$$PID_FRONTEND:frontend:0\n" > .lint-tmp/pids; \
	TOTAL=7; COMPLETED=0; FAIL=0; SPIN=0; \
	printf "\033[?25l"; \
	while [ $$COMPLETED -lt $$TOTAL ]; do \
		SPIN=$$(($$SPIN + 1)); \
		case $$(($$SPIN % 10)) in \
			0) CHAR="⠋" ;; 1) CHAR="⠙" ;; 2) CHAR="⠹" ;; 3) CHAR="⠸" ;; 4) CHAR="⠼" ;; \
			5) CHAR="⠴" ;; 6) CHAR="⠦" ;; 7) CHAR="⠧" ;; 8) CHAR="⠇" ;; 9) CHAR="⠏" ;; \
		esac; \
		printf "\r🚀 Running: "; \
		grep -v "^DONE:" .lint-tmp/pids > .lint-tmp/pids.active 2>/dev/null || touch .lint-tmp/pids.active; \
		while IFS=: read -r PID NAME IGNORE_FAIL || [ -n "$$PID" ]; do \
			[ -z "$$PID" ] && continue; \
			if ! kill -0 $$PID 2>/dev/null; then \
				wait $$PID; EXIT_CODE=$$?; \
				printf "\r\033[K"; \
				echo "--- $$NAME (done) ---"; \
				cat .lint-tmp/$$NAME.log; \
				echo ""; \
				if [ "$$IGNORE_FAIL" != "1" ] && [ $$EXIT_CODE -ne 0 ]; then \
					FAIL=$$(($$FAIL + 1)); \
				fi; \
				sed -i "s/^$$PID:$$NAME:$$IGNORE_FAIL$$/DONE:$$PID:$$NAME:$$IGNORE_FAIL/" .lint-tmp/pids; \
				COMPLETED=$$(($$COMPLETED + 1)); \
			else \
				printf "%s" "$$CHAR $$NAME  "; \
			fi; \
		done < .lint-tmp/pids.active; \
		sleep 0.1; \
	done; \
	printf "\r\033[K"; \
	printf "\033[?25h"; \
	rm -rf .lint-tmp; \
	echo "=== All linting complete: $$FAIL check(s) failed ==="; \
	exit $$FAIL

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

# =============================================================================
# Docker Cleanup Commands
# =============================================================================

# Show Docker disk usage summary
docker-status:
	@echo "📊 Docker Disk Usage Summary:"
	@docker system df
	@echo ""
	@echo "💾 Reclaimable Resources:"
	@echo "  Images:  $(shell docker images -f dangling=true -q | wc -l) dangling images"
	@echo "  Volumes: $(shell docker volume ls -f dangling=true -q | wc -l) unused volumes"
	@echo "  Cache:   $(shell docker system df --format '{{.Reclaimable}}' | tail -1)"

# Quick cleanup - removes dangling images only (safe, can run frequently)
docker-cleanup:
	@echo "🧹 Cleaning up dangling Docker images..."
	@docker image prune -f
	@echo "✅ Cleanup complete!"
	@echo ""
	@$(MAKE) docker-status

# Full cleanup - removes all unused Docker resources (aggressive)
docker-cleanup-full:
	@echo "⚠️  WARNING: This will remove:"
	@echo "  • All dangling images"
	@echo "  • All unused volumes"
	@echo "  • All unused build cache"
	@echo ""
	@read -p "Continue? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		echo "🧹 Cleaning up all unused Docker resources..."; \
		docker image prune -f; \
		docker volume prune -f; \
		docker builder prune -f; \
		echo "✅ Full cleanup complete!"; \
		echo ""; \
		$(MAKE) docker-status; \
	else \
		echo "❌ Cleanup cancelled."; \
	fi

# Remove only old build cache (keeps recent builds)
docker-cleanup-cache:
	@echo "🧹 Cleaning up Docker build cache older than 7 days..."
	@docker builder prune -f --filter "until=168h"
	@echo "✅ Build cache cleanup complete!"
