.PHONY: build-and-publish dev setup migrate createsuperuser test-migrations install clean test lint docker-build docker-run docker-stop dev-api dev-frontend dev-worker

# Main development command - starts all services
dev:
	python dev.py

# Individual service development commands
dev-api:
	PYTHONPATH=api python api/run.py

dev-frontend:
	cd frontend && yarn dev

dev-worker:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python api/manage.py run_huey

# Huey queue management
clear-huey-queue:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python api/manage.py shell -c "from huey.contrib.djhuey import HUEY; HUEY.flush(); print('Huey queue cleared')"

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

# Database management
migrate:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python api/manage.py migrate

createsuperuser:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python api/manage.py createsuperuser

# Testing
test: test-api test-frontend

test-api:
	PYTHONPATH=api python -m pytest api/tests/ api/src/tests/ -v --cov=api/src --cov=api/library_manager --cov-report=html --cov-report=term-missing

test-api-unit:
	PYTHONPATH=api python -m pytest api/tests/unit/ api/src/tests/ -v -m "not integration"

test-api-integration:
	PYTHONPATH=api python -m pytest api/tests/integration/test_simple_integration.py -v

test-api-integration-full:
	PYTHONPATH=api python -m pytest api/tests/integration/ -v -m integration

test-api-integration-isolated:
	PYTHONPATH=api python -m pytest api/tests/integration/test_isolated_integration.py -v

test-api-coverage:
	PYTHONPATH=api python -m pytest api/tests/ api/src/tests/ --cov=api/src --cov=api/library_manager --cov-report=html --cov-report=term-missing --cov-fail-under=80

test-frontend:
	cd frontend && yarn test:run

test-frontend-watch:
	cd frontend && yarn test

test-frontend-coverage:
	cd frontend && yarn test:coverage

test-frontend-ui:
	cd frontend && yarn test:ui

test-migrations:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python api/manage.py showmigrations

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
	cd api && python -m flake8 --config=../.flake8

lint-api-black:
	cd api && python -m black --check --diff .

lint-api-isort:
	cd api && python -m isort --check-only --diff .

lint-api-mypy:
	cd api && python -m mypy src/ library_manager/ --config-file ../pyproject.toml

lint-api-bandit:
	cd api && python -m bandit -r src/ library_manager/ -f json -o bandit-report.json || true

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
	cd frontend && npm run check-newlines

fix-newlines-frontend:
	cd frontend && npm run fix-newlines
