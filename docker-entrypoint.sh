#!/bin/sh
set -e
uv run alembic upgrade head
PORT="${PORT:-8000}"
exec uv run uvicorn zapcart_api.main:app --host 0.0.0.0 --port "$PORT"
