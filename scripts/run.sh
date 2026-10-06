#!/usr/bin/env bash
set -e

PORT="${PORT:-8000}"
echo "=== Starting PharmaCare Development Server on port $PORT ==="
python manage.py runserver 0.0.0.0:$PORT
