"""
Achievements seed data for DianaBot
Populates the achievements table with initial data
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.connection import get_db
from database.models import Achievement


def seed_achievements():
    """Seed initial achievements data"""
    db = next(get_db())
    
    try:
        # Check if achievements already exist
        existing_count = db.query(Achievement).count()
        if existing_count > 0:
            print(f"Found {existing_count} existing achievements, skipping seed")
            return
        
        # Define initial achievements
        achievements_data = [
            {
                "achievement_key": "first_decision",
                "name": "Primera Decisión",
                "description": "Completa tu primer fragmento con decisión",
                "icon_emoji": "🎯",
                "points": 10,
                "reward_besitos": 25,
                "reward_item_id": None,
                "unlock_conditions": {"fragments_completed": 1}
            },
            {
                "achievement_key": "novice_collector",
                "name": "Coleccionista Novato",
                "description": "Posee 5 items en tu inventario",
                "icon_emoji": "📦",
                "points": 15,
                "reward_besitos": 50,
                "reward_item_id": None,
                "unlock_conditions": {"items_owned": 5}
            },
            {
                "achievement_key": "millionaire",
                "name": "Millonario",
                "description": "Acumula 1000 besitos lifetime",
                "icon_emoji": "💰",
                "points": 20,
                "reward_besitos": 100,
                "reward_item_id": None,
                "unlock_conditions": {"lifetime_besitos": 1000}
            },
            {
                "achievement_key": "dedicated",
                "name": "Dedicado",
                "description": "Completa 5 misiones diarias",
                "icon_emoji": "🏆",
                "points": 25,
                "reward_besitos": 75,
                "reward_item_id": None,
                "unlock_conditions": {"daily_missions_completed": 5}
            },
            {
                "achievement_key": "explorer",
                "name": "Explorador",
                "description": "Completa nivel 1 de la narrativa",
                "icon_emoji": "🗺️",
                "points": 30,
                "reward_besitos": 150,
                "reward_item_id": None,
                "unlock_conditions": {"narrative_level": 1}
            }
        ]
        
        # Create achievement objects
        achievements = []
        for data in achievements_data:
            achievement = Achievement(**data)
            achievements.append(achievement)
        
        # Add to database
        db.add_all(achievements)
        db.commit()
        
        print(f"✅ Seeded {len(achievements)} achievements")
        
    except Exception as e:
        print(f"❌ Error seeding achievements: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_achievements()