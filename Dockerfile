# Multi-stage optimized Dockerfile for smaller image sizes
# Target sizes: Production ~600MB (down from ~1GB), Dev ~800MB

# =============================================================================
# Stage 1: Frontend Build (only runs when frontend changes)
# =============================================================================
FROM node:20-alpine AS frontend-build
WORKDIR /frontend

# Install yarn
RUN apk add --no-cache yarn

# Copy package files first for better caching
COPY frontend/package.json frontend/yarn.lock ./

# Install dependencies with cache mount
RUN --mount=type=cache,target=/usr/local/share/.cache/yarn,id=yarn-cache,sharing=locked \
    yarn install --frozen-lockfile --production=false

# Copy source code and build
COPY frontend/ ./
RUN yarn build

# =============================================================================
# Stage 2: FFmpeg static binary (avoids heavy apt dependencies)
# =============================================================================
FROM alpine:3.20 AS ffmpeg-builder

# Download static FFmpeg binary - much smaller than apt install
# This avoids pulling in libllvm15 (114MB), libicu (36MB), and other heavy deps
ARG TARGETARCH
RUN apk add --no-cache curl \
    && mkdir -p /ffmpeg \
    && case "${TARGETARCH}" in \
         amd64) ARCH_NAME="x64" ;; \
         arm64) ARCH_NAME="arm64" ;; \
         *)     ARCH_NAME="x64" ;; \
       esac \
    && echo "Downloading FFmpeg for linux-${ARCH_NAME}..." \
    && curl -fL "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffmpeg-linux-${ARCH_NAME}" -o /ffmpeg/ffmpeg \
    && curl -fL "https://github.com/eugeneware/ffmpeg-static/releases/download/b6.1.1/ffprobe-linux-${ARCH_NAME}" -o /ffmpeg/ffprobe \
    && chmod +x /ffmpeg/ffmpeg /ffmpeg/ffprobe \
    && /ffmpeg/ffmpeg -version

# =============================================================================
# Stage 3: Python Base Image (minimal runtime dependencies)
# =============================================================================
FROM python:3.13-slim-bookworm AS python-base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy static FFmpeg binaries (no apt dependencies needed!)
COPY --from=ffmpeg-builder /ffmpeg/ffmpeg /usr/local/bin/ffmpeg
COPY --from=ffmpeg-builder /ffmpeg/ffprobe /usr/local/bin/ffprobe

# Copy deno binary for yt-dlp JavaScript execution
COPY --from=denoland/deno:bin-2.5.6 /deno /usr/local/bin/deno

# Install minimal system dependencies
# libmediainfo is needed for pymediainfo, ca-certificates for HTTPS
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt-get update \
    && apt-get install -y --no-install-recommends \
       libmediainfo0v5 \
       ca-certificates \
       curl \
    && rm -rf /var/lib/apt/lists/*

# Verify binaries work
RUN ffmpeg -version && deno --version

# =============================================================================
# Stage 4: Python Production Dependencies
# =============================================================================
FROM python-base AS python-deps-prod

COPY requirements.txt ./

# Install production dependencies only
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-compile -r requirements.txt \
    # Remove unnecessary files to reduce size
    && find /usr/local/lib/python3.13/site-packages -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -type d -name tests -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -type d -name test -exec rm -rf {} + 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -name "*.pyc" -delete 2>/dev/null || true \
    && find /usr/local/lib/python3.13/site-packages -name "*.pyo" -delete 2>/dev/null || true \
    # Remove pip after installation (not needed at runtime)
    && pip uninstall -y pip setuptools wheel 2>/dev/null || true

# =============================================================================
# Stage 5: Python Development Dependencies
# =============================================================================
FROM python-base AS python-deps-dev

COPY requirements.txt requirements-dev.txt ./

# Install all dependencies including dev tools
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt -r requirements-dev.txt

# =============================================================================
# Stage 6: Application Code (shared layer)
# =============================================================================
FROM python-base AS app-code

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
# Stage 7: Production Backend (minimal, optimized)
# =============================================================================
FROM python-deps-prod AS backend-prod

# Copy application code
COPY --from=app-code /app /app

# Copy built frontend static files
COPY --from=frontend-build /frontend/dist /app/frontend-dist

# Collect static files and clean up
RUN python manage.py collectstatic --noinput \
    && find /app -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true \
    && find /app -type f -name "*.pyc" -delete 2>/dev/null || true

EXPOSE 5000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]

# =============================================================================
# Stage 8: Development Backend (with dev dependencies and hot reload)
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
# Stage 9: Test Backend (for CI/CD)
# =============================================================================
FROM python-deps-dev AS backend-test

# Copy application code
COPY --from=app-code /app /app

# Copy test-specific files
COPY ./api/tests /app/tests
COPY ./api/pytest.ini /app/pytest.ini
COPY ./api/docker_test_settings.py /app/docker_test_settings.py

# =============================================================================
# Default target is production
# =============================================================================
FROM backend-prod
