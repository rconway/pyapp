#!/usr/bin/env bash

if [ -n "$1" ]; then
  TAG=":$1"
else
  "$(dirname "$0")"/build.sh
fi

PORT="${PORT:-8000}"

docker run --rm -p "$PORT:$PORT" -e PORT="${PORT}" -v "${PWD}/.env:/app/.env" "ghcr.io/rconway/pyapp${TAG}"
