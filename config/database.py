"""
DianaBot - Database Configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis
from .settings import settings


# PostgreSQL Configuration
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=300,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# MongoDB Configuration
def get_mongo_client():
    client = MongoClient(
        host=settings.mongo_host,
        port=settings.mongo_port,
        serverSelectionTimeoutMS=5000
    )
    return client


def get_narrative_db():
    client = get_mongo_client()
    return client[settings.mongo_db]


# Redis Configuration
def get_redis_client():
    return redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        password=settings.redis_password,
        db=settings.redis_db,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
        retry_on_timeout=True
    )


# Dependency functions for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()