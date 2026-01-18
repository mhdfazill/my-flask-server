"""
WallMagic Backend - FastAPI Application
Main entry point for the application.
"""

import os
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.config import settings
from app.database import init_db
from app.routes.auth_routes import router as auth_router


# ============= Lifespan =============

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    print(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down...")


# ============= Application =============

app = FastAPI(
    title=settings.app_name,
    description="Backend API for WallMagic - A Flutter Mobile Wallpaper App",
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============= CORS Middleware =============

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= Global Exception Handler =============

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred",
            "error": str(exc) if settings.debug else "Internal Server Error",
            "path": str(request.url.path)
        }
    )


# ============= Response Models =============

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    app_name: str
    version: str
    timestamp: str


class RootResponse(BaseModel):
    """Root endpoint response model."""
    message: str
    app_name: str
    version: str
    docs_url: str
    health_url: str


# ============= Core Routes =============

@app.get("/", response_model=RootResponse, tags=["Core"])
async def root():
    """
    Root endpoint.
    Returns basic API information and useful links.
    """
    return RootResponse(
        message="Welcome to WallMagic API",
        app_name=settings.app_name,
        version=settings.app_version,
        docs_url="/docs",
        health_url="/health"
    )


@app.get("/health", response_model=HealthResponse, tags=["Core"])
async def health_check():
    """
    Health check endpoint.
    Used by cloud providers to verify the application is running.
    """
    return HealthResponse(
        status="healthy",
        app_name=settings.app_name,
        version=settings.app_version,
        timestamp=datetime.utcnow().isoformat()
    )


# ============= Include Routers =============

app.include_router(auth_router)


# ============= Run Application =============

if __name__ == "__main__":
    import uvicorn
    
    # Get port from environment (Render sets this)
    port = int(os.environ.get("PORT", settings.port))
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=port,
        reload=settings.debug
    )
