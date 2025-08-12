.PHONY: build-and-publish dev dev-container dev-container-down dev-container-logs dev-container-logs-web dev-container-logs-frontend dev-container-logs-worker setup migrate createsuperuser test-migrations install clean test lint docker-build docker-run docker-stop dev-api dev-frontend dev-worker

# Main development command - starts all services
dev:
	python dev.py

# Dev container: run compose with optional local override if present
dev-container:
	@if [ -f docker-compose.override.yml ]; then \
		docker compose up --build; \
	else \
		cp docker-compose.override.example.yml docker-compose.override.yml && echo "Created local override from example"; \
		docker compose up --build; \
	fi

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
	cd api && python manage.py run_huey

# Django admin server (separate from main dev setup)
dev-admin:
	cd api && python manage.py collectstatic --noinput
	cd api && python manage.py runserver 0.0.0.0:8000

# FastAPI server (alternative to dev-api)
dev-fastapi:
	cd api && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Huey queue management
clear-huey-queue:
	cd api && python manage.py shell -c "from huey.contrib.djhuey import HUEY; HUEY.flush(); print('Huey queue cleared')"

# Installation and setup
setup:
	# Install API dependencies
	pip install -r requirements.txt
	# Install frontend dependencies
	yarn install

install-api:
	pip install -r requirements.txt

install-frontend:
	cd frontend && yarn install

install: install-api install-frontend

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

test-api:
	PYTHONPATH=.:api python -m pytest api/tests/ api/src/tests/ -v --cov=api/src --cov=api/library_manager --cov-report=html --cov-report=term-missing

test-api-unit:
	PYTHONPATH=.:api python -m pytest api/tests/unit/ api/src/tests/ -v -m "not integration"

test-api-integration:
	PYTHONPATH=.:api python -m pytest api/tests/integration/test_simple_integration.py -v

test-api-integration-full:
	PYTHONPATH=.:api python -m pytest api/tests/integration/ -v -m integration

test-api-integration-isolated:
	PYTHONPATH=.:api python -m pytest api/tests/integration/test_isolated_integration.py -v

test-api-coverage:
	PYTHONPATH=.:api python -m pytest api/tests/ api/src/tests/ --cov=api/src --cov=api/library_manager --cov-report=html --cov-report=term-missing --cov-fail-under=80

# Convenience alias
test-backend: test-api

test-frontend:
	cd frontend && yarn test:run

test-frontend-watch:
	cd frontend && yarn test

test-frontend-coverage:
	cd frontend && yarn test:coverage

test-frontend-ui:
	cd frontend && yarn test:ui

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
	cd api && python -m flake8 --extend-ignore=W503 --exclude=.venv,__pycache__,node_modules

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

# Code formatting
format: format-api format-frontend

format-api: format-api-black format-api-isort

format-api-black:
	cd api && python -m black .

format-api-isort:
	cd api && python -m isort .

# Auto-fix linting issues
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
	docker build -t spotify-library-manager .

docker-run:
	docker-compose up

docker-stop:
	docker-compose down

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
