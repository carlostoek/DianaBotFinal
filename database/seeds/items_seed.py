#!/usr/bin/env python3
"""
Item seeders for testing the inventory system
Based on Phase 4 requirements: 5 collectibles, 3 consumables, 2 narrative items
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from database.connection import get_db, engine
from database.models import Item


def seed_items():
    """Seed basic items for testing"""
    
    items_data = [
        # 5 Collectibles (Coleccionables)
        {
            "item_key": "fragmento_espejo_1",
            "name": "Fragmento de Espejo Antiguo (1/5)",
            "description": "Un fragmento brillante de un espejo antiguo. Parece ser parte de algo más grande.",
            "item_type": "collectible",
            "rarity": "rare",
            "price_besitos": 50,
            "item_metadata": {"set": "espejo_antiguo", "part": 1, "total_parts": 5}
        },
        {
            "item_key": "fragmento_espejo_2",
            "name": "Fragmento de Espejo Antiguo (2/5)",
            "description": "Segundo fragmento del espejo misterioso. Brilla con luz tenue.",
            "item_type": "collectible",
            "rarity": "rare",
            "price_besitos": 50,
            "item_metadata": {"set": "espejo_antiguo", "part": 2, "total_parts": 5}
        },
        {
            "item_key": "foto_diana_joven",
            "name": "Foto de Diana Joven",
            "description": "Una fotografía descolorida de Diana en su juventud. Parece feliz.",
            "item_type": "collectible",
            "rarity": "epic",
            "price_besitos": 100,
            "item_metadata": {"category": "fotos", "era": "juventud"}
        },
        {
            "item_key": "pluma_lucien",
            "name": "Pluma Estilográfica de Lucien",
            "description": "Una elegante pluma estilográfica que perteneció a Lucien. Aún tiene tinta.",
            "item_type": "collectible",
            "rarity": "epic",
            "price_besitos": 150,
            "item_metadata": {"category": "objetos_personales", "owner": "lucien"}
        },
        {
            "item_key": "collar_perdido",
            "name": "Collar Perdido",
            "description": "Un delicado collar con un dije en forma de corazón. Parece valioso.",
            "item_type": "collectible",
            "rarity": "legendary",
            "price_besitos": 200,
            "item_metadata": {"category": "joyeria", "material": "oro"}
        },
        
        # 3 Consumables (Consumibles)
        {
            "item_key": "pocion_doble_besitos",
            "name": "Poción de Doble Besitos",
            "description": "Duplica los besitos ganados por 1 hora. ¡Perfecta para misiones!",
            "item_type": "consumable",
            "rarity": "rare",
            "price_besitos": 75,
            "item_metadata": {"effect": "double_besitos", "duration": 3600}
        },
        {
            "item_key": "caramelo_energia",
            "name": "Caramelo de Energía",
            "description": "Un dulce caramelo que te da energía para continuar tu aventura.",
            "item_type": "consumable",
            "rarity": "common",
            "price_besitos": 25,
            "item_metadata": {"effect": "restore_energy", "amount": 10}
        },
        {
            "item_key": "te_fortuna",
            "name": "Té de la Fortuna",
            "description": "Un té aromático que mejora tu suerte temporalmente.",
            "item_type": "consumable",
            "rarity": "epic",
            "price_besitos": 120,
            "item_metadata": {"effect": "increase_luck", "duration": 1800}
        },
        
        # 2 Narrative Items (Items Narrativos)
        {
            "item_key": "llave_attico",
            "name": "Llave del Ático Prohibido",
            "description": "Una llave antigua y oxidada. Dicen que abre el ático prohibido de la mansión.",
            "item_type": "narrative_key",
            "rarity": "epic",
            "price_besitos": 0,  # No se puede comprar
            "item_metadata": {"unlocks": "attic_chapter", "required_level": 5}
        },
        {
            "item_key": "diario_diana_joven",
            "name": "Diario de Diana Joven",
            "description": "Un diario personal de Diana en su juventud. Contiene secretos profundos.",
            "item_type": "narrative_key",
            "rarity": "legendary",
            "price_besitos": 0,  # No se puede comprar
            "item_metadata": {"unlocks": "youth_memories", "required_items": ["foto_diana_joven"]}
        },
        
        # Bonus: Power-ups (Mejoras)
        {
            "item_key": "intuicion_lucien",
            "name": "Intuición de Lucien",
            "description": "Revela las consecuencias de tus decisiones por 3 usos.",
            "item_type": "power_up",
            "rarity": "epic",
            "price_besitos": 180,
            "item_metadata": {"effect": "reveal_consequences", "uses": 3}
        }
    ]
    
    db: Session = next(get_db())
    
    try:
        # Clear existing items (for testing)
        db.query(Item).delete()
        
        # Create items
        for item_data in items_data:
            item = Item(**item_data)
            db.add(item)
        
        db.commit()
        print(f"✅ Seeded {len(items_data)} items successfully!")
        
        # Print summary
        print("\n📦 Items seeded:")
        for item in db.query(Item).all():
            print(f"  - {item.name} ({item.item_type}, {item.rarity})")
            
    except Exception as e:
        print(f"❌ Error seeding items: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_items()