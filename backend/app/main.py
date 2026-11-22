"""
SarkariSach - Citizen Cyber Defense & Official Notice Verification Engine.
Production FastAPI application.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.core.rate_limit import limiter
from app.models.database import init_db
from app.api import analyze, check_url, media, tts, complaint, dashboard


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure database tables exist
    init_db()
    yield
    # Shutdown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "SarkariSach is an open-source AI and heuristic verification platform helping Indian citizens "
        "detect digital-arrest calls, fake police/CBI warrants, malicious APK links, and phishing scams. "
        "DISCLAIMER: Guidance provided is for informational awareness only and does not constitute formal legal counsel."
    ),
    lifespan=lifespan
)

# SlowAPI Rate Limiting setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers under /api
app.include_router(analyze.router, prefix=settings.API_V1_STR)
app.include_router(check_url.router, prefix=settings.API_V1_STR)
app.include_router(media.router, prefix=settings.API_V1_STR)
app.include_router(tts.router, prefix=settings.API_V1_STR)
app.include_router(complaint.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Service health and readiness check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "disclaimer": "Informational guidance only, not legal advice."
    }


frontend_dist = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if (frontend_dist / "index.html").is_file():
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
