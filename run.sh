#!/usr/bin/env bash

BIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

"${BIN_DIR}"/create-venv.sh
source "${BIN_DIR}"/venv/bin/activate
trap deactivate EXIT

uvicorn src.main:app --app-dir "${BIN_DIR}" --host 0.0.0.0 --port 8000
