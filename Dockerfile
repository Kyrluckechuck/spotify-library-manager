FROM node:20-alpine AS frontend-build
WORKDIR /frontend
RUN apk add --no-cache yarn
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile
COPY frontend/ ./
RUN yarn build

FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System dependencies
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    ffmpeg \
    mediainfo \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt /app/requirements.txt
COPY requirements-dev.txt /app/requirements-dev.txt
ARG INSTALL_DEV_DEPS=false
RUN if [ "$INSTALL_DEV_DEPS" = "true" ]; then \
      pip install -r /app/requirements.txt -r /app/requirements-dev.txt; \
    else \
      pip install -r /app/requirements.txt; \
    fi

# App source
COPY ./api/ /app/

# Copy built frontend (served by FastAPI static files)
COPY --from=frontend-build /frontend/dist /app/frontend-dist

# Collect static files (no prompts)
RUN python manage.py collectstatic --noinput

EXPOSE 5000

# Default command runs FastAPI via uvicorn; override in compose as needed
# Create non-root user and prepare dirs
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser \
 && mkdir -p /config /config/db /mnt/music_spotify /app/frontend-dist \
 && chown -R appuser:appgroup /app /config /mnt/music_spotify

USER appuser

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "5000"]
