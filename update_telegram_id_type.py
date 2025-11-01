"""
Migration script to update telegram_id from Integer to BigInteger
This fixes the "integer out of range" error for large Telegram IDs
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine
from sqlalchemy import text


def update_telegram_id_type():
    """Update telegram_id columns from Integer to BigInteger"""
    
    with engine.connect() as conn:
        try:
            print("🔄 Updating telegram_id columns to BigInteger...")
            
            # Update users table
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN telegram_id TYPE BIGINT
            """))
            print("✅ Updated users.telegram_id to BIGINT")
            
            # Update event_logs table
            conn.execute(text("""
                ALTER TABLE event_logs 
                ALTER COLUMN telegram_id TYPE BIGINT
            """))
            print("✅ Updated event_logs.telegram_id to BIGINT")
            
            conn.commit()
            print("✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration error: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    update_telegram_id_type()