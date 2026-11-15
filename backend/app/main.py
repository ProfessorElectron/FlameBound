"""FastAPI application for strict, deterministic FlameBound scientific tools."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.app.api.atmosphere import router as atmosphere_router
from backend.app.version import API_SCHEMA_VERSION

app = FastAPI(title="FlameBound API", version=API_SCHEMA_VERSION)
app.include_router(atmosphere_router)


def _error(code: str, field: str | None, message: str) -> dict[str, object]:
    return {
        "status": "error",
        "api_schema_version": API_SCHEMA_VERSION,
        "error": {"code": code, "field": field, "message": message},
    }


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Compatibility health check retained from the original scaffold."""
    return {"status": "ok"}


@app.get("/api/health", tags=["health"])
def api_health_check() -> dict[str, object]:
    """Report process and module availability, not evidence or prediction readiness."""
    return {
        "status": "ok",
        "components": {"atmospheric_engine": "available"},
        "api_schema_version": API_SCHEMA_VERSION,
    }


@app.exception_handler(RequestValidationError)
async def request_validation_error_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    del request
    first_error = exc.errors()[0] if exc.errors() else {}
    location = first_error.get("loc", ())
    field = ".".join(str(item) for item in location if item not in {"body", "query"}) or None
    return JSONResponse(
        status_code=422,
        content=_error(
            "invalid_request",
            field,
            "Request fields must use finite JSON numbers, supported values, and the documented schema.",
        ),
    )


@app.exception_handler(HTTPException)
async def http_error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    del request
    details = exc.detail if isinstance(exc.detail, dict) else {}
    return JSONResponse(
        status_code=exc.status_code,
        content=_error(
            str(details.get("code", "request_unavailable")),
            details.get("field"),
            str(details.get("message", "The requested operation is unavailable.")),
        ),
    )


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Keep internal failures distinguishable from invalid client requests."""
    del request, exc
    return JSONResponse(
        status_code=500,
        content=_error("internal_error", None, "An internal server error occurred."),
    )
