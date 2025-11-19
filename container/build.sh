#!/usr/bin/env bash

CONTAINER_DIR="$(dirname "$0")"

docker build -f "$CONTAINER_DIR"/Dockerfile -t ghcr.io/rconway/authapp "$CONTAINER_DIR"/..
