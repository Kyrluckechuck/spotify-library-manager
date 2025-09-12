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

# Wait for database to be ready with retries
echo "🔄 Waiting for database to be ready..."
for i in {1..30}; do
    if python -c "
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('Database connection successful')
    sys.exit(0)
except Exception as e:
    print(f'Database not ready (attempt $i/30): {e}')
    sys.exit(1)
" 2>/dev/null; then
        echo "✅ Database is ready!"
        break
    fi
    echo "🔄 Database not ready yet (attempt $i/30)..."
    if [ $i -eq 30 ]; then
        echo "❌ Database failed to become ready after 30 attempts"
        exit 1
    fi
    sleep 2
done

# Run migration with generous timeout for large production databases
# SQLite migrations can take a very long time with large datasets (30+ minutes for 100k+ records)
MIGRATION_TIMEOUT=${MIGRATION_TIMEOUT:-7200}  # Default 2 hours, configurable via env var
echo "🔄 Starting SQLite migration with ${MIGRATION_TIMEOUT}s timeout..."

if run_with_timeout "$MIGRATION_TIMEOUT" "python manage.py migrate_from_sqlite --verbosity=2"; then
    echo "✅ SQLite migration complete."
else
    echo "⚠️ SQLite migration timed out after ${MIGRATION_TIMEOUT}s or failed."
    echo "⚠️ For very large databases, consider increasing MIGRATION_TIMEOUT environment variable."
    echo "⚠️ Running basic Django migrations instead..."
    if run_with_timeout 300 "python manage.py migrate --verbosity=2"; then
        echo "✅ Basic Django migrations complete."
    else
        echo "❌ All migration attempts failed!"
        exit 1
    fi
fi

echo "🌐 Starting uvicorn server on ${HOST:-0.0.0.0}:${PORT:-5000}"
exec uvicorn src.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-5000} --log-level info --access-log
