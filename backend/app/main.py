"""
SamadhanX FastAPI Application

Main entry point for the SamadhanX backend API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.db.database import engine
from app.models import base  # Import all models to ensure they are registered


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print("🚀 Starting SamadhanX API...")
    
    # TODO: Initialize database tables
    # TODO: Setup AI services
    # TODO: Initialize external service connections
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SamadhanX API...")


# Create FastAPI application instance
app = FastAPI(
    title="SamadhanX API",
    description="Jharkhand Societal Innovation Exchange - Connecting citizens, universities, and industry for societal impact",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint for health checks."""
    return {
        "message": "SamadhanX API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "status": "healthy"
    }


# TODO: Include routers
# from app.routers import auth, users, challenges, universities, projects, industry, analytics, notifications
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
# app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
# app.include_router(challenges.router, prefix="/api/v1/challenges", tags=["Challenges"])
# app.include_router(universities.router, prefix="/api/v1/universities", tags=["Universities"])
# app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])
# app.include_router(industry.router, prefix="/api/v1/industry", tags=["Industry"])
# app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])
# app.include_router(notifications.router, prefix="/api/v1/notifications", tags=["Notifications"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True if settings.ENVIRONMENT == "development" else False,
    )