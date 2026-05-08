#!/usr/bin/env bash
# =============================================================================
# Docker entrypoint — runs once per container start.
# =============================================================================
set -euo pipefail

cd /app/django_auth

echo "[entrypoint] Applying database migrations..."
python manage.py migrate --noinput

echo "[entrypoint] Collecting static files..."
python manage.py collectstatic --noinput

echo "[entrypoint] Starting Gunicorn..."
exec gunicorn django_auth.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 60 \
    --access-logfile - \
    --error-logfile -
