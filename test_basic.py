#!/usr/bin/env python3
"""
Basic test to verify the project structure and imports work correctly
"""

try:
    # Test configuration import
    from config.settings import settings
    print("✓ Configuration system imported successfully")
    
    # Test database connections
    from database.connection import engine, mongo_db, redis_client
    print("✓ Database connections imported successfully")
    
    # Test API
    from api.main import app
    print("✓ API imported successfully")
    
    print("\n✅ All basic imports working correctly!")
    print("\nProject structure is ready for development.")
    print("Next steps:")
    print("1. Copy .env.example to .env and configure your settings")
    print("2. Run 'docker-compose up -d' to start services")
    print("3. Begin implementing FASE 1: Bot Básico y Sistema de Usuarios")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")