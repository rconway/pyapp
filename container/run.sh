#!/usr/bin/env bash

BIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

if [ -n "$1" ]; then
  TAG=":$1"
else
  "${BIN_DIR}"/build.sh
fi

PORT="${PORT:-8000}"

GREEN=$'\033[32m'
BOLD_RED=$'\033[1;31m'
RESET=$'\033[0m'

docker run --rm --env-file "${BIN_DIR}"/../.env  -p "$PORT:$PORT" -e PORT="${PORT}" "ghcr.io/rconway/pyapp${TAG}" 2>&1 \
  | sed --unbuffered "/Uvicorn running on/a\\${GREEN}INFO${RESET}:     ${BOLD_RED}For local access use http://127.0.0.1:8000${RESET}"
