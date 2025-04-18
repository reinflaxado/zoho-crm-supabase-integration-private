import logging
from fastapi import FastAPI
from app.config import settings
from app.api.webhooks import router as webhook_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="A webhook receiver that connects Zoho CRM to Supabase",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Include routers
app.include_router(webhook_router, prefix="/api/webhooks", tags=["webhooks"])

@app.get("/", tags=["status"])
async def root():
    """Root endpoint to check if the API is running."""
    return {"status": "online", "message": "Zoho CRM to Supabase Integration API"}

@app.get("/health", tags=["status"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.HOST}:{settings.PORT}")
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    ) 