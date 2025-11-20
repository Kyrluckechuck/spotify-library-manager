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

# Install dependencies with cache mount (this layer will be cached unless package files change)
# Share cache with frontend Dockerfile using cache ID
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn,id=yarn-cache,sharing=locked \
    yarn install --frozen-lockfile --production=false

# Copy source code (this layer will be rebuilt when frontend code changes)
COPY frontend/ ./

# Build frontend (this layer will be rebuilt when frontend code changes)
RUN yarn build

# =============================================================================
# Stage 2: Python Base Image (shared base for all Python stages)
# =============================================================================
FROM python:3.13-slim-bookworm AS python-base

# Copy deno binary from official deno image (for yt-dlp JavaScript execution)
COPY --from=denoland/deno:bin-2.5.6 /deno /usr/local/bin/deno

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install system dependencies (this layer rarely changes)
# Use cache mounts for apt to speed up builds
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
 && apt-get install -y --no-install-recommends \
    ffmpeg \
    mediainfo \
    ca-certificates \
    curl

# Verify deno installation
RUN deno --version

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
# Stage 5: Application Code (shared layer to avoid duplication)
# =============================================================================
FROM python-base AS app-code

# Copy application source code (single source of truth)
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
# Stage 6: Production Backend (minimal, optimized)
# =============================================================================
FROM python-deps AS backend-prod

# Copy only application code (no dev dependencies)
COPY --from=app-code /app /app

# Copy built frontend (static files only, no node_modules)
COPY --from=frontend-build /frontend/dist /app/frontend-dist

# Collect static files
RUN python manage.py collectstatic --noinput \
    # Clean up unnecessary files to reduce image size
    && find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /app -type f -name "*.pyc" -delete

EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]

# =============================================================================
# Stage 7: Development Backend (with dev dependencies and hot reload)
# =============================================================================
FROM python-deps-dev AS backend-dev

# Copy application code
COPY --from=app-code /app /app

# Copy built frontend
COPY --from=frontend-build /frontend/dist /app/frontend-dist

# Collect static files
RUN python manage.py collectstatic --noinput

EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000", "--reload"]

# =============================================================================
# Stage 8: Test Backend (for CI/CD)
# =============================================================================
FROM python-deps-dev AS backend-test

# Copy application code
COPY --from=app-code /app /app

# Copy test-specific files
COPY ./api/tests /app/tests
COPY ./api/pytest.ini /app/pytest.ini
COPY ./api/docker_test_settings.py /app/docker_test_settings.py

# Default target is production
FROM backend-prod
