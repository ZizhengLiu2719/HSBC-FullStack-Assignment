"""
FastAPI Application Entry Point

Main application setup with routes, middleware, and configuration.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api import accounts, payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager
    
    Runs on startup and shutdown:
    - Startup: Initialize database tables
    - Shutdown: Cleanup (if needed)
    """
    # Startup
    print("="*60)
    print(f"Starting {settings.APP_NAME} v{settings.VERSION}")
    print("="*60)
    
    # Initialize database tables
    await init_db()
    
    print(f"[OK] Server running on http://{settings.HOST}:{settings.PORT}")
    print(f"[OK] API docs: http://{settings.HOST}:{settings.PORT}/docs")
    print("="*60)
    
    yield  # Application runs here
    
    # Shutdown
    print("\n[INFO] Shutting down application...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="HSBC Full-Stack Assignment - Payment Management System",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)


# ============================================================
# CORS Configuration
# ============================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# ============================================================
# Include Routers
# ============================================================
app.include_router(accounts.router)
app.include_router(payments.router)


# ============================================================
# Root Endpoint
# ============================================================
@app.get("/")
async def root():
    """
    Root endpoint - API health check
    
    Returns:
        API status and version info
    """
    return {
        "name": settings.APP_NAME,
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "endpoints": {
            "accounts": "/api/accounts",
            "payments": "/api/payments"
        }
    }


# ============================================================
# Health Check Endpoint
# ============================================================
@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring
    
    Returns:
        Service health status
    """
    return {
        "status": "healthy",
        "version": settings.VERSION
    }
