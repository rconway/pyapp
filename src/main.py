from fastapi import FastAPI, HTTPException
from starlette.middleware.sessions import SessionMiddleware

from auth_routes import (
    SECRET_KEY,
    auth_router,
    custom_http_exception_handler,
    get_current_user,
    get_user_profile,
    is_production,
)
from core_routes import create_core_router
from metrics_routes import metrics_router, prometheus_middleware

app = FastAPI()

# Session middleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    https_only=is_production,
    same_site="lax",
    max_age=60 * 60 * 24 * 7,
)

app.middleware("http")(prometheus_middleware)
app.include_router(metrics_router)
app.include_router(auth_router)
app.include_router(create_core_router(get_current_user, get_user_profile))
app.add_exception_handler(HTTPException, custom_http_exception_handler)
