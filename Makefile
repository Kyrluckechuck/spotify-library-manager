.PHONY: build-and-publish dev setup migrate createsuperuser test-migrations install clean test lint docker-build docker-run docker-stop dev-api dev-frontend dev-worker

# Main development command - starts all services
dev:
	python dev.py

# Individual service development commands
dev-api:
	PYTHONPATH=api python run.py

dev-frontend:
	yarn dev

dev-worker:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python manage.py run_huey

# Installation and setup
setup:
	# Install API dependencies
	$(shell which python) setup_simple.py
	# Install frontend dependencies
	yarn install

install-api:
	pip install -r requirements.txt

install-frontend:
	yarn install

install: install-api install-frontend

# Database management
migrate:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python manage.py migrate

createsuperuser:
	PYTHONPATH=api DJANGO_SETTINGS_MODULE=settings python manage.py createsuperuser

# Testing
test: test-api test-frontend

test-api:
	PYTHONPATH=api python -m pytest test_api.py

test-frontend:
	yarn test

test-migrations:
	python test_migrations.py

# Linting
lint: lint-api lint-frontend

lint-api:
	cd api && python -m flake8

lint-frontend:
	yarn lint

# Building
build: build-frontend

build-frontend:
	yarn build

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
