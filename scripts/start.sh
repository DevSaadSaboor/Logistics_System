#!/usr/bin/env sh
set -eu

PORT="${PORT:-8000}"

echo "Running database migrations..."
alembic upgrade head

echo "Starting uvicorn on 0.0.0.0:${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"
