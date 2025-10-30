#!/usr/bin/env python3
"""
Script para agregar columnas faltantes a las tablas de base de datos
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine
from sqlalchemy import text

def add_missing_columns():
    """Add missing columns to database tables"""
    
    try:
        print("🔄 Agregando columnas faltantes a las tablas...")
        
        with engine.connect() as conn:
            # Agregar is_starting_fragment a narrative_fragments
            try:
                conn.execute(text("""
                    ALTER TABLE narrative_fragments 
                    ADD COLUMN IF NOT EXISTS is_starting_fragment BOOLEAN DEFAULT FALSE
                """))
                print("✅ Columna 'is_starting_fragment' agregada a narrative_fragments")
            except Exception as e:
                print(f"⚠️  Error agregando is_starting_fragment: {e}")
            
            # Agregar updated_at a user_narrative_progress
            try:
                conn.execute(text("""
                    ALTER TABLE user_narrative_progress 
                    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                """))
                print("✅ Columna 'updated_at' agregada a user_narrative_progress")
            except Exception as e:
                print(f"⚠️  Error agregando updated_at: {e}")
            
            # Agregar description a narrative_fragments si no existe
            try:
                conn.execute(text("""
                    ALTER TABLE narrative_fragments 
                    ADD COLUMN IF NOT EXISTS description TEXT
                """))
                print("✅ Columna 'description' agregada a narrative_fragments")
            except Exception as e:
                print(f"⚠️  Error agregando description: {e}")
            
            conn.commit()
            
        print("✅ Migración de columnas completada exitosamente!")
        
    except Exception as e:
        print(f"❌ Error en la migración: {e}")
        sys.exit(1)

if __name__ == "__main__":
    add_missing_columns()