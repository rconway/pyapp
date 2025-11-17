
"$(dirname "$0")"/build.sh

docker run --rm -p 8000:8000 -v $PWD/.env:/app/.env ghcr.io/rconway/authapp
