"""
Main FastAPI application entry point for SLV Housing Market.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .database import engine, Base

# Import routers
from .routers import properties, ai_chat, trends, property_ai

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    debug=settings.DEBUG,
    description="Salt Lake Valley Housing Market Web Application",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "SLV Housing Market API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "database": "connected",
        "data_source": settings.DATA_SOURCE
    }


# Include routers
app.include_router(properties.router, prefix="/api/properties", tags=["properties"])
app.include_router(ai_chat.router, prefix="/api/ai", tags=["ai"])
app.include_router(trends.router, prefix="/api/trends", tags=["trends"])
app.include_router(property_ai.router, prefix="/api/property-ai", tags=["property-ai"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
