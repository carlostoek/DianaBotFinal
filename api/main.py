from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.connection import get_db
import redis

# Import routers
from api.routers.auth import router as auth_router
from api.routers.config import router as config_router
from api.routers.users import router as users_router
from api.routers.content import router as content_router
from api.routers.analytics import router as analytics_router
from api.routers.dashboard import router as dashboard_router

app = FastAPI(title="DianaBot API", version="1.0.0")

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(config_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")


@app.get("/")
async def root():
    return {"message": "DianaBot API is running"}


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test PostgreSQL connection
        db.execute(text("SELECT 1")).scalar()
        
        # Test Redis connection
        redis_client = redis.Redis(host="localhost", port=6379, db=0)
        redis_client.ping()
        
        return {
            "status": "healthy",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }


@app.get("/info")
async def info():
    """API information"""
    return {
        "name": "DianaBot",
        "version": "1.0.0",
        "description": "Sistema de Telegram con narrativa ramificada y gamificación"
    }