"""
Observability middleware for request tracking.
"""
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from app.utils.logging import logger


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Middleware for request logging and timing."""

    async def dispatch(self, request: Request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        logger.info("Request started", extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
        })

        response = await call_next(request)
        duration = time.time() - start

        logger.info("Request completed", extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        })

        response.headers["X-Request-ID"] = request_id
        return response