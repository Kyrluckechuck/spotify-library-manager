# Multi-stage optimized Dockerfile for better caching
# This Dockerfile separates frontend and backend builds for optimal caching

# =============================================================================
# Stage 1: Frontend Build (only runs when frontend changes)
# =============================================================================
FROM node:20-alpine AS frontend-build
WORKDIR /frontend

# Install yarn
RUN apk add --no-cache yarn

# Copy package files first for better caching
COPY frontend/package.json frontend/yarn.lock ./

# Install dependencies (this layer will be cached unless package files change)
RUN yarn install --frozen-lockfile --production=false

# Copy source code (this layer will be rebuilt when frontend code changes)
COPY frontend/ ./

# Build frontend (this layer will be rebuilt when frontend code changes)
RUN yarn build

# =============================================================================
# Stage 2: Python Base Image (shared base for all Python stages)
# =============================================================================
FROM python:3.13-slim-bookworm AS python-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (this layer rarely changes)
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ffmpeg \
    mediainfo \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# =============================================================================
# Stage 3: Python Dependencies (cached unless requirements change)
# =============================================================================
FROM python-base AS python-deps

# Copy requirements files first for better caching
COPY requirements.txt requirements-dev.txt ./

# Install Python dependencies with cache mount
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

# =============================================================================
# Stage 4: Development Dependencies (optional)
# =============================================================================
FROM python-deps AS python-deps-dev
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements-dev.txt

# =============================================================================
# Stage 5: Application Code (rebuilds when source changes)
# =============================================================================
FROM python-deps AS app-base

# Copy application source code
COPY ./api/src /app/src
COPY ./api/downloader /app/downloader
COPY ./api/lib /app/lib
COPY ./api/library_manager /app/library_manager
COPY ./api/celery_app.py /app/celery_app.py
COPY ./api/celery_beat_schedule.py /app/celery_beat_schedule.py
COPY ./api/manage.py /app/manage.py
COPY ./api/urls.py /app/urls.py
COPY ./api/settings.py /app/settings.py
COPY ./api/run.py /app/run.py
COPY ./api/scripts /app/scripts

# Make startup script executable
RUN chmod +x /app/scripts/startup.sh

# =============================================================================
# Stage 6: Production Backend (final image)
# =============================================================================
FROM python-deps AS backend-prod

# Copy application source code
COPY ./api/src /app/src
COPY ./api/downloader /app/downloader
COPY ./api/lib /app/lib
COPY ./api/library_manager /app/library_manager
COPY ./api/celery_app.py /app/celery_app.py
COPY ./api/celery_beat_schedule.py /app/celery_beat_schedule.py
COPY ./api/manage.py /app/manage.py
COPY ./api/urls.py /app/urls.py
COPY ./api/settings.py /app/settings.py
COPY ./api/run.py /app/run.py
COPY ./api/scripts /app/scripts

# Make startup script executable
RUN chmod +x /app/scripts/startup.sh

# Copy built frontend from frontend-build stage
COPY --from=frontend-build /frontend/dist /app/frontend-dist

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]

# =============================================================================
# Stage 7: Development Backend (with dev dependencies)
# =============================================================================
FROM python-deps-dev AS backend-dev

# Copy application source code
COPY ./api/src /app/src
COPY ./api/downloader /app/downloader
COPY ./api/lib /app/lib
COPY ./api/library_manager /app/library_manager
COPY ./api/celery_app.py /app/celery_app.py
COPY ./api/celery_beat_schedule.py /app/celery_beat_schedule.py
COPY ./api/manage.py /app/manage.py
COPY ./api/urls.py /app/urls.py
COPY ./api/settings.py /app/settings.py
COPY ./api/run.py /app/run.py
COPY ./api/scripts /app/scripts

# Make startup script executable
RUN chmod +x /app/scripts/startup.sh

# Copy built frontend from frontend-build stage
COPY --from=frontend-build /frontend/dist /app/frontend-dist

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]

# =============================================================================
# Stage 8: Test Backend (for CI/CD)
# =============================================================================
FROM python-deps-dev AS backend-test

# Copy application source code
COPY ./api/src /app/src
COPY ./api/downloader /app/downloader
COPY ./api/lib /app/lib
COPY ./api/library_manager /app/library_manager
COPY ./api/celery_app.py /app/celery_app.py
COPY ./api/celery_beat_schedule.py /app/celery_beat_schedule.py
COPY ./api/manage.py /app/manage.py
COPY ./api/urls.py /app/urls.py
COPY ./api/settings.py /app/settings.py
COPY ./api/run.py /app/run.py
COPY ./api/scripts /app/scripts
COPY ./api/tests /app/tests
COPY ./api/pytest.ini /app/pytest.ini
COPY ./api/docker_test_settings.py /app/docker_test_settings.py

# Make startup script executable
RUN chmod +x /app/scripts/startup.sh

# Default target is production
FROM backend-prod
