#!/usr/bin/env bash

"$(dirname "$0")"/create-venv.sh

source "$(dirname "$0")"/venv/bin/activate
trap deactivate EXIT

uvicorn src.main:app --host 0.0.0.0 --port 8000
