#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
while ! python -c "import socket; s=socket.socket(); s.settimeout(2); s.connect(('db',5432)); s.close()" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready."

# Ensure FLASK_APP is set for CLI commands
export FLASK_APP=run:app

# Initialize migrations folder if it doesn't exist
if [ ! -d "migrations" ]; then
    echo "Initializing migrations..."
    flask db init
fi

echo "Running database migrations..."
flask db upgrade

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 "run:app"
