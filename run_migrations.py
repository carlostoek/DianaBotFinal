#!/usr/bin/env python3
"""
Run database migrations for DianaBot
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine, Base
from database.models import *


def run_migrations():
    """Create all database tables"""
    try:
        print("🔄 Running database migrations...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database migrations completed successfully!")
        print("✅ Tables created: users")
        
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_migrations()