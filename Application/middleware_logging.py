"""Request id y logging estructurado de peticiones HTTP."""

import json
import logging
import time
import uuid
from typing import Any, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("bytte.api")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        req_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = req_id
        t0 = time.perf_counter()

        response = await call_next(request)

        ms = (time.perf_counter() - t0) * 1000.0
        log_line: dict[str, Any] = {
            "event": "http_request",
            "request_id": req_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(ms, 2),
        }
        if hasattr(request.state, "principal_kind"):
            log_line["principal_kind"] = request.state.principal_kind
            log_line["principal_sub"] = getattr(request.state, "principal_sub", None)
            log_line["principal_restaurant_id"] = getattr(
                request.state, "principal_restaurant_id", None
            )

        logger.info(json.dumps(log_line, ensure_ascii=False))
        response.headers["X-Request-ID"] = req_id
        return response
