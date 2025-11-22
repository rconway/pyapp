#!/usr/bin/env bash

if [ -n "$1" ]; then
  TAG=":$1"
else
  "$(dirname "$0")"/build.sh
fi

docker run --rm -p 8000:8000 -v $PWD/.env:/app/.env "ghcr.io/rconway/pyapp${TAG}"
