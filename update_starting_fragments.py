#!/usr/bin/env python3
"""
Script para marcar fragmentos iniciales en la base de datos
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import engine
from sqlalchemy import text

def update_starting_fragments():
    """Mark starting fragments in the database"""
    
    try:
        print("🔄 Marcando fragmentos iniciales...")
        
        with engine.connect() as conn:
            # Marcar fragmentos iniciales para cada nivel
            # Nivel 1: fragment_1_1
            conn.execute(text("""
                UPDATE narrative_fragments 
                SET is_starting_fragment = TRUE 
                WHERE fragment_key = 'fragment_1_1'
            """))
            print("✅ Fragmento 'fragment_1_1' marcado como inicial para Nivel 1")
            
            # Nivel 2: fragment_2_1  
            conn.execute(text("""
                UPDATE narrative_fragments 
                SET is_starting_fragment = TRUE 
                WHERE fragment_key = 'fragment_2_1'
            """))
            print("✅ Fragmento 'fragment_2_1' marcado como inicial para Nivel 2")
            
            # Nivel 3: intro_3
            conn.execute(text("""
                UPDATE narrative_fragments 
                SET is_starting_fragment = TRUE 
                WHERE fragment_key = 'intro_3'
            """))
            print("✅ Fragmento 'intro_3' marcado como inicial para Nivel 3")
            
            conn.commit()
            
        print("✅ Fragmentos iniciales actualizados exitosamente!")
        
    except Exception as e:
        print(f"❌ Error actualizando fragmentos iniciales: {e}")
        sys.exit(1)

if __name__ == "__main__":
    update_starting_fragments()