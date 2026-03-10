#!/usr/bin/env bash

BIN_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"

VENV_DIR="${BIN_DIR}"/venv

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    exit 0
fi

python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install -U pip
pip install -U -r requirements.txt
deactivate
