.PHONY: build-and-publish dev setup migrate createsuperuser test-migrations

build-and-publish:
	sudo podman build -t test_build .
	sudo podman tag test_build ghcr.io/kyrluckechuck/spotify-library-manager:latest
	sudo podman push ghcr.io/kyrluckechuck/spotify-library-manager:latest

setup:
	# Install API dependencies
	cd api && $(shell which python) scripts/setup_simple.py
	# Install frontend dependencies
	cd frontend && yarn install

dev:
	python dev.py

migrate:
	cd api && python manage.py migrate

createsuperuser:
	cd api && python manage.py createsuperuser

test-migrations:
	python test_migrations.py
