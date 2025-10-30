from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.connection import get_db
import redis

app = FastAPI(title="DianaBot API", version="1.0.0")


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