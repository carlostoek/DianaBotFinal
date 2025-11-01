#!/usr/bin/env python3
"""
Migration script to fix telegram_id column types from INTEGER to BIGINT
"""

from database.connection import engine, SessionLocal
from sqlalchemy import text

def fix_telegram_id_columns():
    """Change telegram_id columns from INTEGER to BIGINT"""
    
    print("Starting migration: Fixing telegram_id column types...")
    
    with engine.connect() as conn:
        # Check current column types
        print("\nCurrent column types:")
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name IN ('users', 'event_logs') 
            AND column_name = 'telegram_id'
        """))
        
        for row in result:
            print(f"  {row.table_name}.{row.column_name}: {row.data_type}")
        
        # Update users.telegram_id to BIGINT
        print("\nUpdating users.telegram_id to BIGINT...")
        conn.execute(text("ALTER TABLE users ALTER COLUMN telegram_id TYPE BIGINT"))
        
        # Update event_logs.telegram_id to BIGINT  
        print("Updating event_logs.telegram_id to BIGINT...")
        conn.execute(text("ALTER TABLE event_logs ALTER COLUMN telegram_id TYPE BIGINT"))
        
        # Commit the changes
        conn.commit()
        
        # Verify the changes
        print("\nVerifying column types after migration:")
        result = conn.execute(text("""
            SELECT table_name, column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name IN ('users', 'event_logs') 
            AND column_name = 'telegram_id'
        """))
        
        for row in result:
            print(f"  {row.table_name}.{row.column_name}: {row.data_type}")
        
        print("\n✅ Migration completed successfully!")

if __name__ == "__main__":
    fix_telegram_id_columns()