"""Minimal API entry point; feature routes are added by the backend owner."""

from fastapi import FastAPI

app = FastAPI(title="FlameBound API", version="0.1.0")


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Return a basic process health response."""
    return {"status": "ok"}
