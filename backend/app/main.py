"""
Main FastAPI Application
Production-grade setup with security, monitoring, and middleware
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
from typing import Dict
from pathlib import Path
import os

# ALLOW OAUTH OVER HTTP/LOCALHOST FOR DEV
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from app.config import settings
from app.database import init_db, close_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await init_db()
        logger.info("Database initialized")
        
        # Initialize lesson cache
        from app.core.cache import init_cache
        init_cache(redis_client=None)  # Memory cache (upgrade to Redis for production)
        logger.info("Lesson cache initialized (memory mode)")
    except Exception as e:
        logger.error(f"STARTUP ERROR: {e}")
        # Dont crash, just log.
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await close_db()
    logger.info("Database connections closed")

# ...

# GZip compression
# app.add_middleware(GZipMiddleware, minimum_size=1000)


# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade API for AI-powered lesson generation",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    openapi_url="/api/openapi.json" if settings.DEBUG else None,
    lifespan=lifespan
)


from starlette.middleware.sessions import SessionMiddleware

# ... imports ...

# ===== Middleware Configuration =====

# Session Middleware (Required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    https_only=not settings.DEBUG  # Secure in production
)

# CORS Configuration - Allow all for local development  
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    max_age=3600,
)

# GZip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Mount static files
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")


# ===== Root Endpoints =====

@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs" if settings.DEBUG else "disabled"
    }


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint for load balancers"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION
    }


# ===== API Router Registration =====

from app.api.v1 import auth, lessons, debug, profile, history # New routers

# Include routers with API v1 prefix
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(profile.router, prefix="/api/v1/users", tags=["Profile"])
app.include_router(history.router, prefix="/api/v1/lessons", tags=["History"]) # History matched first
app.include_router(lessons.router, prefix="/api/v1/lessons", tags=["Lessons"]) # Lessons wildcard last
app.include_router(debug.router, prefix="/api/v1/debug", tags=["Debug"])

# ===== Static Files for Downloads =====

# Create outputs directory if it doesn't exist
outputs_dir = Path("outputs")
outputs_dir.mkdir(exist_ok=True)

# Mount static files for PPT/PDF downloads
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
logger.info("Static files mounted at /outputs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )
