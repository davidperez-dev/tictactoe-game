#!/usr/bin/env bash
# =============================================================================
# Docker entrypoint — runs once per container start.
# =============================================================================
set -euo pipefail

SERVICE_NAME="tictactoe"

cd /app/${SERVICE_NAME}

echo "[entrypoint] Applying database migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

echo "[entrypoint] Starting Gunicorn..."
exec gunicorn ${SERVICE_NAME}.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
