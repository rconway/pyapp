from fastapi import FastAPI, Request, Depends
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
    userinfo_endpoint="https://api.github.com/user",
    client_kwargs={"scope": "user:email"},
)


@app.get("/world")
async def world():
    return {"message": "Hello, World!"}


@app.get("/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth")
    return await oauth.github.authorize_redirect(request, redirect_uri)


@app.get("/auth")
async def auth(request: Request):
    token = await oauth.github.authorize_access_token(request)
    # GitHub doesn’t return ID token, so fetch user info manually
    resp = await oauth.github.get("https://api.github.com/user", token=token)
    user_info = resp.json()
    request.session["user"] = user_info
    return RedirectResponse(url="/hello")


def get_current_user(request: Request):
    user = request.session.get("user")
    if not user:
        return None
    return user


@app.get("/hello")
async def hello(request: Request):
    user = get_current_user(request)
    if not user:
        return RedirectResponse(url="/login")
    return {"message": f"Hello, {user['login']}!"}
