from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from pathlib import Path
from typing import Any
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
OAUTH_REDIRECT_BASE_URL = os.getenv("OAUTH_REDIRECT_BASE_URL", "").strip().rstrip("/")
PROVIDER_SETTINGS = {
    "github": {
        "protocol": "oauth2",
        "label": "GitHub",
        "oauth_client": "github",
        "userinfo_endpoint": "https://api.github.com/user",
        "authorize_url": "https://github.com/login/oauth/authorize",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "client_id_env": "GITHUB_CLIENT_ID",
        "client_secret_env": "GITHUB_CLIENT_SECRET",
        "scope": "user:email",
    },
    "google": {
        "protocol": "oidc",
        "label": "Google",
        "oauth_client": "google",
        "server_metadata_url": "https://accounts.google.com/.well-known/openid-configuration",
        "client_id_env": "GOOGLE_CLIENT_ID",
        "client_secret_env": "GOOGLE_CLIENT_SECRET",
        "scope": "openid profile email",
    },
    # Example OIDC provider (disabled by default):
    # "example_oidc": {
    #     "protocol": "oidc",
    #     "label": "Example OIDC",
    #     "oauth_client": "example_oidc",
    #     "server_metadata_url": "https://example.com/.well-known/openid-configuration",
    #     # Optional: if omitted, ID token claims are used.
    #     # "userinfo_endpoint": "https://example.com/oauth2/userinfo",
    #     "client_id_env": "EXAMPLE_OIDC_CLIENT_ID",
    #     "client_secret_env": "EXAMPLE_OIDC_CLIENT_SECRET",
    #     "scope": "openid profile email",
    # },
}

AUTH_PROVIDERS = {
    provider: {
        "protocol": config.get("protocol", "oauth2"),
        "label": config["label"],
        "oauth_client": config["oauth_client"],
        "userinfo_endpoint": config.get("userinfo_endpoint"),
        "client_id": os.getenv(config["client_id_env"]),
        "client_secret": os.getenv(config["client_secret_env"]),
        "authorize_url": config.get("authorize_url"),
        "access_token_url": config.get("access_token_url"),
        "server_metadata_url": config.get("server_metadata_url"),
        "scope": config["scope"],
        "client_id_env": config["client_id_env"],
        "client_secret_env": config["client_secret_env"],
    }
    for provider, config in PROVIDER_SETTINGS.items()
}

missing_env_vars = ["SECRET_KEY"] if not SECRET_KEY else []
for provider_config in AUTH_PROVIDERS.values():
    if not provider_config["client_id"]:
        missing_env_vars.append(provider_config["client_id_env"])
    if not provider_config["client_secret"]:
        missing_env_vars.append(provider_config["client_secret_env"])

if missing_env_vars:
    raise RuntimeError(
        "Missing required environment variables: " + ", ".join(sorted(missing_env_vars))
    )

environment = os.getenv("ENVIRONMENT", "development").strip().lower()
is_production = environment in {"production", "prod"}
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI()

# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=is_production,
    same_site="lax",
    max_age=60 * 60 * 24 * 7,
)

# OAuth setup
oauth = OAuth()
for provider, provider_config in AUTH_PROVIDERS.items():
    register_kwargs = {
        "name": provider_config["oauth_client"],
        "client_id": provider_config["client_id"],
        "client_secret": provider_config["client_secret"],
        "client_kwargs": {"scope": provider_config["scope"]},
    }

    protocol = provider_config["protocol"]
    if protocol == "oauth2":
        if (
            not provider_config["authorize_url"]
            or not provider_config["access_token_url"]
        ):
            raise RuntimeError(
                f"Provider '{provider}' requires authorize_url and access_token_url for oauth2"
            )
        register_kwargs["authorize_url"] = provider_config["authorize_url"]
        register_kwargs["access_token_url"] = provider_config["access_token_url"]
        if provider_config["userinfo_endpoint"]:
            register_kwargs["userinfo_endpoint"] = provider_config["userinfo_endpoint"]
    elif protocol == "oidc":
        if not provider_config["server_metadata_url"]:
            raise RuntimeError(
                f"Provider '{provider}' requires server_metadata_url for oidc"
            )
        register_kwargs["server_metadata_url"] = provider_config["server_metadata_url"]
    else:
        raise RuntimeError(
            f"Provider '{provider}' has unsupported protocol '{protocol}'"
        )

    oauth.register(**register_kwargs)


def get_provider_config(provider: str) -> dict[str, Any]:
    config = AUTH_PROVIDERS.get(provider)
    if not config:
        raise HTTPException(status_code=404, detail="Unknown identity provider")
    return config


def get_provider_client(provider_config: dict[str, Any]):
    client = oauth.create_client(provider_config["oauth_client"])
    if client is None:
        raise HTTPException(status_code=501, detail="Provider not implemented")
    return client


def build_oauth_redirect_uri(request: Request, provider: str) -> str:
    callback = request.url_for("auth_provider", provider=provider)
    callback_url = str(callback)
    callback_path = callback.path

    # Allow explicit override for reverse proxies or deployed environments.
    if OAUTH_REDIRECT_BASE_URL:
        return f"{OAUTH_REDIRECT_BASE_URL}{callback_path}"

    return callback_url


async def fetch_user_info(
    provider: str,
    provider_config: dict[str, Any],
    client: Any,
    request: Request,
    token: dict[str, Any],
) -> dict[str, Any]:
    protocol = provider_config["protocol"]
    if protocol == "oauth2":
        userinfo_endpoint = provider_config.get("userinfo_endpoint")
        if not userinfo_endpoint:
            raise HTTPException(
                status_code=500,
                detail=f"Provider '{provider}' missing userinfo_endpoint",
            )
        resp = await client.get(userinfo_endpoint, token=token)
        return resp.json()

    if protocol == "oidc":
        userinfo_endpoint = provider_config.get("userinfo_endpoint")
        if userinfo_endpoint:
            resp = await client.get(userinfo_endpoint, token=token)
            return resp.json()

        # Authlib parse_id_token signature differs across versions.
        try:
            claims = await client.parse_id_token(token, nonce=None)
        except TypeError:
            claims = await client.parse_id_token(request, token)
        return dict(claims)

    raise HTTPException(
        status_code=500, detail=f"Unsupported protocol for '{provider}'"
    )


def build_session_user(provider: str, user_info: dict[str, Any]) -> dict[str, Any]:
    # Keep GitHub behavior unchanged for compatibility while making provider explicit.
    if provider == "github":
        return user_info
    return {
        "provider": provider,
        "profile": user_info,
    }


def get_user_profile(user: dict[str, Any]) -> dict[str, Any]:
    # New providers store profile under `profile`; GitHub remains flat for compatibility.
    profile = user.get("profile")
    if isinstance(profile, dict):
        return profile
    return user


@app.get("/world")
async def world():
    return {"message": "Hello, world!"}


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        "login_provider_selector.html",
        {
            "request": request,
            "providers": [
                {"id": provider_id, "label": provider["label"]}
                for provider_id, provider in AUTH_PROVIDERS.items()
            ],
        },
    )


@app.get("/login/{provider}")
async def login_provider(provider: str, request: Request):
    provider_config = get_provider_config(provider)
    client = get_provider_client(provider_config)

    redirect_uri = build_oauth_redirect_uri(request, provider)
    return await client.authorize_redirect(request, redirect_uri)


@app.get("/auth/{provider}")
async def auth_provider(provider: str, request: Request):
    provider_config = get_provider_config(provider)
    client = get_provider_client(provider_config)

    token = await client.authorize_access_token(request)
    user_info = await fetch_user_info(provider, provider_config, client, request, token)
    request.session["user"] = build_session_user(provider, user_info)
    return RedirectResponse(url="/hello")


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    accept = request.headers.get("accept", "")
    if "text/html" in accept:
        return RedirectResponse(url="/world")
    return {"message": "Logged out"}


# Dependency to inject current user
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.get("/hello")
async def hello(user: dict = Depends(get_current_user)):
    profile = get_user_profile(user)
    display_name = (
        profile.get("name")
        or profile.get("login")
        or profile.get("email")
        or profile.get("sub")
    )
    return {"message": f"Hello, {display_name}!"}


@app.get("/me")
async def me(user: dict = Depends(get_current_user)):
    # Return a provider profile shape for new providers while preserving GitHub compatibility.
    return get_user_profile(user)


# Custom exception handler: redirect browsers; JSON for API clients
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
