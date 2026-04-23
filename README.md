# pyapp

Fastapi app with integrated auth providers

## Quickstart

### 1) Configure environment

Create a `.env` file in the repo root:

```env
GITHUB_CLIENT_ID=your_github_oauth_app_client_id
GITHUB_CLIENT_SECRET=your_github_oauth_app_client_secret
GOOGLE_CLIENT_ID=your_google_oauth_client_id
GOOGLE_CLIENT_SECRET=your_google_oauth_client_secret
# Optional example OIDC provider credentials:
# EXAMPLE_OIDC_CLIENT_ID=your_example_oidc_client_id
# EXAMPLE_OIDC_CLIENT_SECRET=your_example_oidc_client_secret
SECRET_KEY=your_generated_secret
ENVIRONMENT=development
# Optional: force OAuth callback base URL (useful behind proxies)
# OAUTH_REDIRECT_BASE_URL=https://your-domain.example
```

Generate a strong session secret with:

```bash
./gen_secret_key.sh
```

For your GitHub OAuth app, use this callback URL during local development:

`http://127.0.0.1:8000/auth/github`

For your Google OAuth client, use this callback URL during local development:

`http://127.0.0.1:8000/auth/google`

If your app runs behind a proxy/load balancer, set `OAUTH_REDIRECT_BASE_URL`
so provider callbacks use the externally visible HTTPS host.

For additional providers, use the same pattern: `/auth/{provider}`.

### 2) Run locally

```bash
./create-venv.sh
./run.sh
```

Local run uses: `uvicorn main:app --app-dir ./src --host 0.0.0.0 --port 8000`.

`./run.sh` prints a local-access hint using `http://127.0.0.1:8000` after the Uvicorn startup line.

### 3) Run in container

```bash
./container/build.sh
PORT=8000 ./container/run.sh
```

Container run uses: `uvicorn main:app` (the Docker image copies `src/` directly to `/app`).

## Endpoints

- `GET /world`: public health endpoint.
- `GET /metrics`: Prometheus scrape endpoint with request count and latency metrics.
- `GET /login`: provider selector page rendered from configured providers.
- `GET /login/github`: starts GitHub OAuth flow.
- `GET /auth/github`: GitHub OAuth callback; stores GitHub profile JSON in session.
- `GET /login/google`: starts Google OAuth flow.
- `GET /auth/google`: Google OAuth callback; stores Google profile JSON in session.
- `GET /logout`: clears session user; redirects browsers to `/world` and returns JSON for API clients.
- `GET /hello`: protected; returns greeting using authenticated user.
- `GET /me`: protected; returns stored provider profile JSON.

## Validation checks

With the app running:

```bash
python -m compileall src
curl -i http://127.0.0.1:8000/world
curl -i http://127.0.0.1:8000/metrics
curl -i http://127.0.0.1:8000/me
curl -i -H 'Accept: text/html' http://127.0.0.1:8000/me
```

Expected unauthenticated behavior for `/me`:

- API client: `401` JSON response.
- HTML client: redirect to `/login` (provider selector page).

## Adding Providers

- Add a provider entry to `PROVIDER_SETTINGS` in `src/auth_routes.py`.
- Required common keys:
	- `label`: display text on the selector page
	- `oauth_client`: registered Authlib client name
	- `client_id_env` and `client_secret_env`
	- `scope`
- For `protocol: oauth2`, configure:
	- `authorize_url`
	- `access_token_url`
	- `userinfo_endpoint`
- For `protocol: oidc`, configure:
	- `server_metadata_url`
	- Optional `userinfo_endpoint` (if omitted, ID token claims are used)
- A ready-to-copy disabled OIDC example is included in `src/auth_routes.py` under `PROVIDER_SETTINGS`.
- OAuth clients are registered automatically from provider settings.
- The generic routes `/login/{provider}` and `/auth/{provider}` handle dispatch.
