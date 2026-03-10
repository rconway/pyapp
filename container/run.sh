#!/usr/bin/env bash

BIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

if [ -n "$1" ]; then
  TAG=":$1"
else
  "${BIN_DIR}"/build.sh
fi

PORT="${PORT:-8000}"

docker run --rm --env-file "${BIN_DIR}"/../.env -p "$PORT:$PORT" -e PORT="${PORT}" "ghcr.io/rconway/pyapp${TAG}"
