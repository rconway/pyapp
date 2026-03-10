# Project Guidelines

## Code Style
- Keep edits small and localized; follow the existing async FastAPI style in `src/main.py`.
- Preserve dependency injection patterns (for example `Depends(get_current_user)`) for protected endpoints.
- Use existing response types (`RedirectResponse`, `JSONResponse`) instead of introducing new abstractions.
- Keep this repo lightweight; do not add new frameworks unless explicitly requested.

## Architecture
- The app is a single FastAPI module: `src/main.py`.
- Public route: `/world`.
- OAuth flow: `/login` starts GitHub auth; `/auth` exchanges token, fetches `https://api.github.com/user`, stores `request.session["user"]`, then redirects to `/hello`.
- Protected routes: `/hello` and `/me` rely on `get_current_user`.
- Preserve 401 behavior: HTML clients (`Accept: text/html`) redirect to `/login`; API clients receive JSON `{"detail": ...}`.

## Build and Test
- Create environment: `./create-venv.sh`
- Run locally: `./run.sh` (starts `uvicorn src.main:app --host 0.0.0.0 --port 8000`)
- Build container: `./container/build.sh`
- Run container: `PORT=8000 ./container/run.sh` (runs `uvicorn main:app`)
- No formal test suite is present; validate changes with:
  - `python -m compileall src`
  - `curl -i http://localhost:8000/world`
  - `curl -i http://localhost:8000/me` (expect 401 JSON when unauthenticated)
  - `curl -i -H 'Accept: text/html' http://localhost:8000/me` (expect redirect to `/login`)

## Project Conventions
- Keep local/container app-path distinction intact: local uses `src.main:app`, container uses `main:app` because `container/Dockerfile` copies `src/` contents directly to `/app`.
- Keep environment loading via `load_dotenv()`; do not hardcode credentials.
- Generate session secrets with `./gen_secret_key.sh`.
- Update Python dependencies in `requirements.txt` only.

## Integration Points
- Auth provider is GitHub OAuth configured via Authlib in `src/main.py`.
- Required environment variables: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`, `SECRET_KEY`.
- Session data stores the GitHub user profile JSON under the `user` key.
- Session middleware depends on a valid `SECRET_KEY` and `itsdangerous` from `requirements.txt`.

## Security
- Never commit `.env` or real secrets.
- `SECRET_KEY` must be high-entropy and treated as required for secure sessions.
- Do not log access tokens, OAuth secrets, or full session payloads.
- Do not weaken auth checks on `/hello` and `/me`.
