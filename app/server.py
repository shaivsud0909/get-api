"""Single-service entrypoint: the API under /api and the built frontend at /.

The frontend is built with VITE_API_BASE_URL=/api, so the browser calls the
API on the same origin. `app.main:app` stays the bare API (tests use it).
"""
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Scope

from app.main import app as api_app

FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", Path(__file__).resolve().parents[1] / "frontend" / "dist"))


class SPAStaticFiles(StaticFiles):
    """Static files with a fallback to index.html for client-side routes."""

    async def get_response(self, path: str, scope: Scope):
        try:
            response = await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            if exc.status_code != 404 or path.startswith("assets/"):
                raise
            response = await super().get_response("index.html", scope)
        if path.startswith("assets/"):
            response.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return response


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.mount("/api", api_app)

if FRONTEND_DIST.is_dir():
    app.mount("/", SPAStaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
