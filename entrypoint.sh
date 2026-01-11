#!/bin/sh

set -eux
export PYTHONUNBUFFERED=1

echo "[entrypoint] starting consumer in background"
poetry run python run.py &

echo "[entrypoint] validating app import"
poetry run python -c "import main; print('[entrypoint] import main ok')" 

echo "[entrypoint] starting uvicorn on ${PORT:-9000}"
exec poetry run uvicorn main:app --host 0.0.0.0 --port "${PORT:-9000}" --log-level info
