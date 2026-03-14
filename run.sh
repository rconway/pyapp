#!/usr/bin/env bash

BIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

"${BIN_DIR}"/create-venv.sh
source "${BIN_DIR}"/venv/bin/activate
trap deactivate EXIT

GREEN=$'\033[32m'
BOLD_RED=$'\033[1;31m'
RESET=$'\033[0m'

uvicorn src.main:app --app-dir "${BIN_DIR}" --host 0.0.0.0 --port 8000 --use-colors 2>&1 \
  | sed --unbuffered "/Uvicorn running on/a\\${GREEN}INFO${RESET}:     ${BOLD_RED}For local access use http://127.0.0.1:8000${RESET}"
