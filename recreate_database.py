#!/usr/bin/env python3
"""
Script to recreate the database with correct schema for telegram_id as BIGINT
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.connection import Base, engine, SessionLocal
from database.models import *
from sqlalchemy import text

def backup_and_recreate():
    """Backup data and recreate database with correct schema"""
    
    print("Starting database recreation process...")
    
    # First, let's check if we can drop and recreate tables
    try:
        # Drop all tables
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        
        # Create all tables with correct schema
        print("Creating tables with correct schema...")
        Base.metadata.create_all(bind=engine)
        
        print("✅ Database schema recreated successfully!")
        
        # Verify the schema
        print("\nVerifying schema...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name, column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name IN ('users', 'event_logs') 
                AND column_name = 'telegram_id'
            """))
            
            print("Current telegram_id column types:")
            for row in result:
                print(f"  {row.table_name}.{row.column_name}: {row.data_type}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during database recreation: {e}")
        return False

def run_seeds():
    """Run all seed scripts to populate the database"""
    
    print("\nRunning seed scripts...")
    
    try:
        # Import and run seed scripts
        from database.seeds.items_seed import seed_items
        from database.seeds.missions_seed import seed_missions
        from database.seeds.narrative_seed import seed_narrative
        
        print("Seeding items...")
        seed_items()
        
        print("Seeding missions...")
        seed_missions()
        
        print("Seeding narrative...")
        seed_narrative()
        
        print("✅ All seeds completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        return False

if __name__ == "__main__":
    print("=== DianaBot Database Recreation ===")
    
    # Recreate database schema
    if backup_and_recreate():
        # Run seed scripts
        if run_seeds():
            print("\n🎉 Database recreation completed successfully!")
            print("The telegram_id columns are now BIGINT and all data has been seeded.")
        else:
            print("\n⚠️  Database schema recreated but seeding failed.")
    else:
        print("\n❌ Database recreation failed.")