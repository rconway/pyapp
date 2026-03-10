# pyapp

Fastapi app with integrated auth providers

## Quickstart

### 1) Configure environment

Create a `.env` file in the repo root:

```env
GITHUB_CLIENT_ID=your_github_oauth_app_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_app_client_secret
SECRET_KEY=your_generated_secret
ENVIRONMENT=development
```

Generate a strong session secret with:

```bash
./gen_secret_key.sh
```

For your GitHub OAuth app, use this callback URL during local development:

`http://localhost:8000/auth`

### 2) Run locally

```bash
./create-venv.sh
./run.sh
```

Local run uses: `uvicorn src.main:app --host 0.0.0.0 --port 8000`.

### 3) Run in container

```bash
./container/build.sh
PORT=8000 ./container/run.sh
```

Container run uses: `uvicorn main:app` (the Docker image copies `src/` directly to `/app`).

## Endpoints

- `GET /world`: public health endpoint.
- `GET /login`: starts GitHub OAuth flow.
- `GET /auth`: OAuth callback; stores GitHub profile JSON in session.
- `GET /logout`: clears session user; redirects browsers to `/world` and returns JSON for API clients.
- `GET /hello`: protected; returns greeting using authenticated user.
- `GET /me`: protected; returns stored GitHub profile JSON.

## Validation checks

With the app running:

```bash
python -m compileall src
curl -i http://localhost:8000/world
curl -i http://localhost:8000/me
curl -i -H 'Accept: text/html' http://localhost:8000/me
```

Expected unauthenticated behavior for `/me`:

- API client: `401` JSON response.
- HTML client: redirect to `/login`.
