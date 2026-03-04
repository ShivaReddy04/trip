#!/bin/bash
set -e

export FLASK_APP=run:app

echo "Running database migrations..."
flask db upgrade

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 300 "run:app"