#!/bin/sh

set -eu

echo "[entrypoint] starting consumer in background"
poetry run python run.py &

echo "[entrypoint] starting uvicorn on ${PORT:-9000}"
exec poetry run uvicorn main:app --host 0.0.0.0 --port "${PORT:-9000}" --log-level info
