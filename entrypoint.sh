#!/bin/sh

set -eu

poetry run python run.py &

exec poetry run uvicorn main:app --host 0.0.0.0 --port "${PORT:-9000}"
