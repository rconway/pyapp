import time

from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "path", "status_code"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
)


async def prometheus_middleware(request: Request, call_next):
    path = request.url.path
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        REQUEST_COUNT.labels(
            method=request.method,
            path=path,
            status_code="500",
        ).inc()
        REQUEST_LATENCY.labels(method=request.method, path=path).observe(
            time.perf_counter() - start_time
        )
        raise

    REQUEST_COUNT.labels(
        method=request.method,
        path=path,
        status_code=str(response.status_code),
    ).inc()
    REQUEST_LATENCY.labels(method=request.method, path=path).observe(
        time.perf_counter() - start_time
    )
    return response


metrics_router = APIRouter()


@metrics_router.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
