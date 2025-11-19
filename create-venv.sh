#!/usr/bin/env bash

VENV_DIR="$(dirname "$0")"/venv

if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
    exit 0
fi

python -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
python -m pip install -U pip
pip install -U -r requirements.txt
deactivate
