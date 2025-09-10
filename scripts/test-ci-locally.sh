#!/bin/bash
set -e

echo "🧪 Testing CI environment locally..."

# Create temporary directories like CI does
CI_TEMP="/tmp/slm-ci-test-$$"
CONFIG_DIR="$CI_TEMP/slm_config"
MUSIC_DIR="$CI_TEMP/slm_music"

echo "📁 Creating temporary directories..."
mkdir -p "$CONFIG_DIR/db" "$MUSIC_DIR"

# Create minimal settings.yaml like CI does
echo "📝 Creating minimal settings.yaml..."
cat > "$CONFIG_DIR/settings.yaml" << 'EOF'
# Minimal CI configuration
default:
  cookies_location: "/config/cookies.txt"
  final_path: "/mnt/music_spotify"
  ALBUM_TYPES_TO_DOWNLOAD:
    - single
    - album
    - compilation
  ALBUM_GROUPS_TO_IGNORE:
    - appears_on
EOF

echo "🧹 Cleaning up any existing containers..."
docker compose down -v 2>/dev/null || true

# Set environment variables like CI does
export SLM_CONFIG_DIR="$CONFIG_DIR"
export MUSIC_DIR="$MUSIC_DIR"
export BACKEND_IMAGE="ghcr.io/kyrluckechuck/spotify-library-manager:latest"
export FRONTEND_IMAGE="ghcr.io/kyrluckechuck/spotify-library-manager-frontend:latest"
export DJANGO_DEBUG="False"
export DJANGO_SECRET_KEY="django-insecure-ci-testing-key"
export AUTH_SECRET_KEY="ci-testing-auth-key"
export POSTGRES_DB="spotify_library_manager"
export POSTGRES_USER="slm_user"
export POSTGRES_PASSWORD="slm_dev_password"

echo "🌍 Environment variables set:"
echo "  CONFIG_DIR: $SLM_CONFIG_DIR"
echo "  MUSIC_DIR: $MUSIC_DIR"
echo "  BACKEND_IMAGE: $BACKEND_IMAGE"
echo "  FRONTEND_IMAGE: $FRONTEND_IMAGE"

echo "🚀 Starting containers..."
docker compose up --build -d

echo "📊 Container status immediately after start:"
docker compose ps

echo "📋 Web container logs (first 15 seconds):"
timeout 15 docker compose logs -f web || echo "Log capture complete"

echo "⏰ Waiting 30 seconds for health checks..."
sleep 30

echo "📊 Container status after wait:"
docker compose ps

echo "🔍 Testing health endpoint directly..."
if curl -s http://localhost:5000/healthz; then
    echo "✅ Health endpoint responding"
else
    echo "❌ Health endpoint not responding"
fi

echo "📋 Final container logs:"
docker compose logs web

# Cleanup function
cleanup() {
    echo "🧹 Cleaning up..."
    docker compose down -v
    rm -rf "$CI_TEMP"
}

# Ask user if they want to keep containers running
echo ""
read -p "Keep containers running for debugging? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    cleanup
else
    echo "🔧 Containers still running. Clean up manually with:"
    echo "  docker compose down -v"
    echo "  rm -rf $CI_TEMP"
fi
