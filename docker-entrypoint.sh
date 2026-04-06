#!/bin/sh
set -e

# docker compose run app <команда> — выполняем как есть (без миграций + uvicorn)
if [ "$#" -gt 0 ] && [ "$1" != "uvicorn" ]; then
  exec "$@"
fi

echo "Running migrations..."
alembic upgrade head
exec "$@"
