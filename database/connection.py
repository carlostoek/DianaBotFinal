from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
import redis
from config.settings import settings

# PostgreSQL connection
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# MongoDB connection
mongo_client = MongoClient(
    f"mongodb://{settings.mongo_host}:{settings.mongo_port}/"
)
mongo_db = mongo_client[settings.mongo_db]

# Redis connection
redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=settings.redis_db,
    decode_responses=True
)


def get_db():
    """Dependency for PostgreSQL database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_mongo():
    """Dependency for MongoDB database"""
    return mongo_db


def get_redis():
    """Dependency for Redis client"""
    return redis_client