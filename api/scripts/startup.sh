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
    print(f'Database not ready (attempt {i}/30): {e}')
    sys.exit(1)
"; then
        echo "✅ Database is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Database failed to become ready after 30 attempts"
        exit 1
    fi
    sleep 2
done

# Run migration with a timeout to prevent hanging
if run_with_timeout 60 "python manage.py migrate_from_sqlite --verbosity=2"; then
    echo "✅ Migrations complete."
else
    echo "⚠️ SQLite migration timed out or failed. Running basic Django migrations instead..."
    if run_with_timeout 60 "python manage.py migrate --verbosity=2"; then
        echo "✅ Basic Django migrations complete."
    else
        echo "❌ All migration attempts failed!"
        exit 1
    fi
fi

echo "🌐 Starting uvicorn server on ${HOST:-0.0.0.0}:${PORT:-5000}"
exec uvicorn src.main:app --host ${HOST:-0.0.0.0} --port ${PORT:-5000} --log-level info --access-log
