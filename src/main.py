from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from authlib.integrations.starlette_client import OAuth
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))

# OAuth setup
oauth = OAuth()
oauth.register(
    name="github",
    client_id=os.getenv("GITHUB_CLIENT_ID"),
    client_secret=os.getenv("GITHUB_CLIENT_SECRET"),
    authorize_url="https://github.com/login/oauth/authorize",
    access_token_url="https://github.com/login/oauth/access_token",
    # GitHub is not OIDC, so we call the API directly
    userinfo_endpoint="https://api.github.com/user",
    client_kwargs={"scope": "user:email"},
)


@app.get("/world")
async def world():
    return {"message": "Hello, world!"}


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/auth")
async def auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    # Explicitly call GitHub API for user info
    resp = await oauth.github.get("https://api.github.com/user", token=token)
    user_info = resp.json()
    request.session["user"] = user_info
    return RedirectResponse(url="/hello")


# Dependency to inject current user
def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.get("/hello")
async def hello(user: dict = Depends(get_current_user)):
    display_name = user.get("name") or user.get("login")
    return {"message": f"Hello, {display_name}!"}


@app.get("/me")
async def me(user: dict = Depends(get_current_user)):
    # Return the full GitHub profile JSON stored in session
    return user


# Custom exception handler: redirect browsers; JSON for API clients
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    if exc.status_code == 401:
        accept = request.headers.get("accept", "")
        if "text/html" in accept:
            return RedirectResponse(url="/login")
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
