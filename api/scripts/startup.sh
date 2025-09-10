#!/bin/bash
set -e

echo "🚀 Starting web service..."

# Function to handle timeouts
run_with_timeout() {
    local timeout=$1
    local cmd="${@:2}"
    
    timeout $timeout bash -c "$cmd" || {
        echo "⚠️ Command timed out after ${timeout}s: $cmd"
        return 1
    }
}

echo "🗄️ Running migrations..."
# Run migration with a timeout to prevent hanging
if run_with_timeout 60 "python manage.py migrate_from_sqlite --verbosity=2"; then
    echo "✅ Migrations complete."
else
    echo "⚠️ Migration timed out or failed. Continuing with server startup..."
    echo "🔧 Running basic Django migrations instead..."
    python manage.py migrate --verbosity=2 || {
        echo "❌ Basic migrations also failed!"
        exit 1
    }
fi

echo "🌐 Starting uvicorn server on ${HOST:-0.0.0.0}:${PORT:-5000}"
exec uvicorn src.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-5000} --log-level info --access-log
