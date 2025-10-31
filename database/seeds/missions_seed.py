"""
Mission seeder for DianaBot
Populates the missions table with initial missions
"""

import logging
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Mission

logger = logging.getLogger(__name__)


def seed_missions():
    """Seed initial missions into the database"""
    db: Session = next(get_db())
    
    try:
        # Check if missions already exist
        existing_missions = db.query(Mission).count()
        if existing_missions > 0:
            logger.info(f"Missions already exist in database ({existing_missions} missions)")
            return
        
        # Initial missions data
        missions_data = [
            {
                "mission_key": "daily_complete_fragment",
                "title": "Explorador Diario",
                "description": "Completa 1 fragmento narrativo",
                "mission_type": "daily",
                "recurrence": "daily",
                "requirements": {"fragments_completed": 1},
                "rewards": {"besitos": 20},
                "is_active": True
            },
            {
                "mission_key": "daily_claim_reward",
                "title": "Recompensa Diaria",
                "description": "Reclama tu regalo diario",
                "mission_type": "daily",
                "recurrence": "daily",
                "requirements": {"daily_reward_claimed": 1},
                "rewards": {"besitos": 10},
                "is_active": True
            },
            {
                "mission_key": "weekly_complete_fragments",
                "title": "Aventurero Semanal",
                "description": "Completa 5 fragmentos esta semana",
                "mission_type": "weekly",
                "recurrence": "weekly",
                "requirements": {"fragments_completed": 5},
                "rewards": {"besitos": 100},
                "is_active": True
            },
            {
                "mission_key": "narrative_reach_level_2",
                "title": "Ascenso Narrativo",
                "description": "Alcanza el nivel 2 en la narrativa",
                "mission_type": "narrative",
                "recurrence": "once",
                "requirements": {"narrative_level": 2},
                "rewards": {"besitos": 50, "items": ["key_mansion_garden"]},
                "is_active": True
            },
            {
                "mission_key": "daily_react_to_posts",
                "title": "Reaccionario",
                "description": "Reacciona a 3 posts en el canal",
                "mission_type": "daily",
                "recurrence": "daily",
                "requirements": {"react_to_posts": 3},
                "rewards": {"besitos": 15},
                "is_active": True
            },
            {
                "mission_key": "weekly_heart_reactor",
                "title": "Corazón de Oro",
                "description": "Reacciona con ❤️ a 10 posts esta semana",
                "mission_type": "weekly",
                "recurrence": "weekly",
                "requirements": {"react_❤️_count": 10},
                "rewards": {"besitos": 75},
                "is_active": True
            }
        ]
        
        # Create mission objects
        missions = []
        for mission_data in missions_data:
            mission = Mission(**mission_data)
            missions.append(mission)
        
        # Add to database
        db.add_all(missions)
        db.commit()
        
        logger.info(f"Successfully seeded {len(missions)} missions")
        
    except Exception as e:
        logger.error(f"Error seeding missions: {e}")
        db.rollback()
        raise


if __name__ == "__main__":
    seed_missions()