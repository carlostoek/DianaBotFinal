#!/usr/bin/env python3
"""
Narrative seeders for testing the narrative system
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import NarrativeLevel, NarrativeFragment


def seed_narrative():
    """Seed narrative levels and fragments for testing"""
    
    db: Session = next(get_db())
    
    try:
        # Update existing narrative levels instead of deleting
        levels_data = [
            {
                "level_key": "level_1_introduction",
                "title": "El Misterio de la Mansión Diana",
                "description": "Tu primera aventura en el mundo de Diana",
                "unlock_conditions": {"min_besitos": 0},  # Available to everyone
                "order_index": 1,
                "is_active": True
            },
            {
                "level_key": "level_2_forest",
                "title": "Secretos del Pasado",
                "description": "Explora los misterios del bosque",
                "unlock_conditions": {
                    "min_besitos": 50,
                    "required_fragments": ["level_1_end"]
                },
                "order_index": 2,
                "is_active": True
            },
            {
                "level_key": "level_3_attic",
                "title": "El Ático Prohibido",
                "description": "Descubre los secretos más oscuros",
                "unlock_conditions": {
                    "min_besitos": 100,
                    "required_items": ["llave_attico"],
                    "required_fragments": ["level_2_end"]
                },
                "order_index": 3,
                "is_active": True
            },
            {
                "level_key": "level_4_vip_exclusive",
                "title": "El Santuario VIP",
                "description": "Contenido exclusivo para miembros VIP",
                "unlock_conditions": {
                    "subscription_required": "vip",
                    "required_fragments": ["level_3_end"]
                },
                "order_index": 4,
                "is_active": True
            }
        ]
        
        for level_data in levels_data:
            existing_level = db.query(NarrativeLevel).filter(
                NarrativeLevel.level_key == level_data["level_key"]
            ).first()
            
            if existing_level:
                # Update existing level
                for key, value in level_data.items():
                    setattr(existing_level, key, value)
            else:
                # Create new level
                level = NarrativeLevel(**level_data)
                db.add(level)
        
        db.commit()
        
        # Get level IDs
        level_1 = db.query(NarrativeLevel).filter(NarrativeLevel.level_key == "level_1_introduction").first()
        level_2 = db.query(NarrativeLevel).filter(NarrativeLevel.level_key == "level_2_forest").first()
        level_3 = db.query(NarrativeLevel).filter(NarrativeLevel.level_key == "level_3_attic").first()
        
        if not all([level_1, level_2, level_3]):
            print("❌ Error: Required levels not found")
            return
        
        # Get or create level 4 VIP
        level_4 = db.query(NarrativeLevel).filter(NarrativeLevel.level_key == "level_4_vip_exclusive").first()
        if not level_4:
            # Create level 4 if it doesn't exist
            level_4 = NarrativeLevel(
                level_key="level_4_vip_exclusive",
                title="El Santuario VIP",
                description="Contenido exclusivo para miembros VIP",
                unlock_conditions={
                    "subscription_required": "vip",
                    "required_fragments": ["level_3_end"]
                },
                order_index=4,
                is_active=True
            )
            db.add(level_4)
            db.commit()
            print("✅ Created VIP level 4")
        
        # Create narrative fragments
        fragments_data = [
            # Level 1 fragments with branching narrative
            {
                "fragment_key": "intro_1",
                "level_id": level_1.id,
                "title": "La Llamada Misteriosa",
                "unlock_conditions": None,
                "order_index": 1,
                "is_active": True
            },
            {
                "fragment_key": "decision_1_a",
                "level_id": level_1.id,
                "title": "Investigar el Ruido",
                "unlock_conditions": {"required_fragments": ["intro_1"]},
                "order_index": 2,
                "is_active": True
            },
            {
                "fragment_key": "decision_1_b",
                "level_id": level_1.id,
                "title": "Ignorar y Seguir",
                "unlock_conditions": {"required_fragments": ["intro_1"]},
                "order_index": 3,
                "is_active": True
            },
            {
                "fragment_key": "consequence_1_a",
                "level_id": level_1.id,
                "title": "Encuentro Inesperado",
                "unlock_conditions": {"required_fragments": ["decision_1_a"]},
                "order_index": 4,
                "is_active": True
            },
            {
                "fragment_key": "consequence_1_b",
                "level_id": level_1.id,
                "title": "Camino Seguro",
                "unlock_conditions": {"required_fragments": ["decision_1_b"]},
                "order_index": 5,
                "is_active": True
            },
            {
                "fragment_key": "level_1_end",
                "level_id": level_1.id,
                "title": "Final del Nivel 1",
                "unlock_conditions": {
                    "required_fragments": ["consequence_1_a", "consequence_1_b"]
                },
                "order_index": 6,
                "is_active": True
            },
            
            # Branching fragments based on narrative flags
            {
                "fragment_key": "trust_lucien_path",
                "level_id": level_1.id,
                "title": "Confianza en Lucien",
                "unlock_conditions": {
                    "narrative_flags": ["trusted_lucien"]
                },
                "order_index": 7,
                "is_active": True
            },
            {
                "fragment_key": "distrust_lucien_path",
                "level_id": level_1.id,
                "title": "Desconfianza en Lucien",
                "unlock_conditions": {
                    "narrative_flags": ["distrusted_lucien"]
                },
                "order_index": 8,
                "is_active": True
            },
            
            # Level 2 fragments
            {
                "fragment_key": "intro_2",
                "level_id": level_2.id,
                "title": "El Diario Encontrado",
                "unlock_conditions": {"required_fragments": ["level_1_end"]},
                "order_index": 1,
                "is_active": True
            },
            {
                "fragment_key": "level_2_end",
                "level_id": level_2.id,
                "title": "Final del Nivel 2",
                "unlock_conditions": {"required_fragments": ["intro_2"]},
                "order_index": 2,
                "is_active": True
            },
            
            # Level 3 fragments (VIP)
            {
                "fragment_key": "intro_3",
                "level_id": level_3.id,
                "title": "El Ático Revelado",
                "unlock_conditions": {
                    "required_fragments": ["level_2_end"],
                    "required_items": ["llave_attico"]
                },
                "order_index": 1,
                "is_active": True
            },
            
            # Additional fragments with specific requirements for Phase 7
            {
                "fragment_key": "secret_chamber",
                "level_id": level_2.id,
                "title": "La Cámara Secreta",
                "unlock_conditions": {
                    "min_besitos": 50,
                    "required_fragments": ["intro_2"]
                },
                "order_index": 3,
                "is_active": True
            },
            {
                "fragment_key": "ancient_treasure",
                "level_id": level_2.id,
                "title": "Tesoro Ancestral",
                "unlock_conditions": {
                    "min_besitos": 50,
                    "required_items": ["mapa_tesoro"]
                },
                "order_index": 4,
                "is_active": True
            },
            {
                "fragment_key": "final_revelation",
                "level_id": level_3.id,
                "title": "La Revelación Final",
                "unlock_conditions": {
                    "required_fragments": ["secret_chamber", "ancient_treasure"],
                    "min_besitos": 100
                },
                "order_index": 2,
                "is_active": True
            },
            
            # Phase 10: Additional branching narrative content
            {
                "fragment_key": "lucien_decision",
                "level_id": level_2.id,
                "title": "La Propuesta de Lucien",
                "unlock_conditions": {
                    "required_fragments": ["intro_2"],
                    "narrative_flags": ["trusted_lucien"]
                },
                "order_index": 5,
                "is_active": True
            },
            {
                "fragment_key": "lucien_betrayal",
                "level_id": level_2.id,
                "title": "La Traición",
                "unlock_conditions": {
                    "required_fragments": ["lucien_decision"],
                    "narrative_flags": ["accepted_lucien_offer"]
                },
                "order_index": 6,
                "is_active": True
            },
            {
                "fragment_key": "lucien_redemption",
                "level_id": level_2.id,
                "title": "La Redención",
                "unlock_conditions": {
                    "required_fragments": ["lucien_decision"],
                    "narrative_flags": ["rejected_lucien_offer"]
                },
                "order_index": 7,
                "is_active": True
            },
            {
                "fragment_key": "diana_alliance",
                "level_id": level_2.id,
                "title": "La Alianza con Diana",
                "unlock_conditions": {
                    "required_fragments": ["intro_2"],
                    "narrative_flags": ["distrusted_lucien"]
                },
                "order_index": 8,
                "is_active": True
            },
            {
                "fragment_key": "neutral_path",
                "level_id": level_2.id,
                "title": "El Camino Neutral",
                "unlock_conditions": {
                    "required_fragments": ["intro_2"],
                    "narrative_flags": []
                },
                "order_index": 9,
                "is_active": True
            },
            
            # Level 3 branching endings
            {
                "fragment_key": "lucien_ending",
                "level_id": level_3.id,
                "title": "Final: El Legado de Lucien",
                "unlock_conditions": {
                    "required_fragments": ["intro_3"],
                    "narrative_flags": ["lucien_path_complete"]
                },
                "order_index": 3,
                "is_active": True
            },
            {
                "fragment_key": "diana_ending",
                "level_id": level_3.id,
                "title": "Final: La Verdad de Diana",
                "unlock_conditions": {
                    "required_fragments": ["intro_3"],
                    "narrative_flags": ["diana_path_complete"]
                },
                "order_index": 4,
                "is_active": True
            },
            {
                "fragment_key": "neutral_ending",
                "level_id": level_3.id,
                "title": "Final: El Observador",
                "unlock_conditions": {
                    "required_fragments": ["intro_3"],
                    "narrative_flags": ["neutral_path_complete"]
                },
                "order_index": 5,
                "is_active": True
            },
            {
                "fragment_key": "secret_ending",
                "level_id": level_3.id,
                "title": "Final Secreto: La Unión",
                "unlock_conditions": {
                    "required_fragments": ["intro_3"],
                    "narrative_flags": ["lucien_path_complete", "diana_path_complete"],
                    "required_items": ["llave_unificacion"]
                },
                "order_index": 6,
                "is_active": True
            },
            
            # Level 4 VIP Exclusive Fragments
            {
                "fragment_key": "vip_intro",
                "level_id": level_4.id,
                "title": "La Invitación VIP",
                "unlock_conditions": {
                    "subscription_required": "vip",
                    "required_fragments": ["level_3_end"]
                },
                "order_index": 1,
                "is_active": True
            },
            {
                "fragment_key": "vip_chamber_secrets",
                "level_id": level_4.id,
                "title": "Secretos de la Cámara VIP",
                "unlock_conditions": {
                    "subscription_required": "vip",
                    "required_fragments": ["vip_intro"]
                },
                "order_index": 2,
                "is_active": True
            },
            {
                "fragment_key": "vip_ancient_artifact",
                "level_id": level_4.id,
                "title": "El Artefacto Ancestral VIP",
                "unlock_conditions": {
                    "subscription_required": "vip",
                    "required_fragments": ["vip_chamber_secrets"],
                    "required_items": ["llave_vip"]
                },
                "order_index": 3,
                "is_active": True
            },
            {
                "fragment_key": "vip_final_revelation",
                "level_id": level_4.id,
                "title": "La Revelación Final VIP",
                "unlock_conditions": {
                    "subscription_required": "vip",
                    "required_fragments": ["vip_ancient_artifact"],
                    "min_besitos": 200
                },
                "order_index": 4,
                "is_active": True
            },
            {
                "fragment_key": "vip_ultimate_ending",
                "level_id": level_4.id,
                "title": "Final Definitivo VIP",
                "unlock_conditions": {
                    "subscription_required": "vip",
                    "required_fragments": ["vip_final_revelation"],
                    "narrative_flags": ["vip_path_complete"]
                },
                "order_index": 5,
                "is_active": True
            },
            
            # Secret fragments (Phase 21)
            {
                "fragment_key": "lucien_backstory",
                "level_id": level_2.id,
                "title": "El Pasado de Lucien",
                "unlock_conditions": {
                    "secret_code_required": True
                },
                "order_index": 10,
                "is_active": True,
                "is_secret": True
            },
            {
                "fragment_key": "prophecy_revealed",
                "level_id": level_2.id,
                "title": "La Profecía Revelada",
                "unlock_conditions": {
                    "secret_code_required": True
                },
                "order_index": 11,
                "is_active": True,
                "is_secret": True
            },
            {
                "fragment_key": "hidden_chamber",
                "level_id": level_3.id,
                "title": "La Cámara Oculta",
                "unlock_conditions": {
                    "secret_code_required": True
                },
                "order_index": 7,
                "is_active": True,
                "is_secret": True
            },
            {
                "fragment_key": "alternate_ending",
                "level_id": level_3.id,
                "title": "Final Alternativo",
                "unlock_conditions": {
                    "secret_code_required": True
                },
                "order_index": 8,
                "is_active": True,
                "is_secret": True
            },
            {
                "fragment_key": "character_secret",
                "level_id": level_4.id,
                "title": "El Secreto del Personaje",
                "unlock_conditions": {
                    "secret_code_required": True
                },
                "order_index": 6,
                "is_active": True,
                "is_secret": True
            }
        ]
        
        for fragment_data in fragments_data:
            existing_fragment = db.query(NarrativeFragment).filter(
                NarrativeFragment.fragment_key == fragment_data["fragment_key"]
            ).first()
            
            if existing_fragment:
                # Update existing fragment
                for key, value in fragment_data.items():
                    setattr(existing_fragment, key, value)
            else:
                # Create new fragment
                fragment = NarrativeFragment(**fragment_data)
                db.add(fragment)
        
        db.commit()
        
        print(f"✅ Seeded {len(levels_data)} narrative levels and {len(fragments_data)} fragments successfully!")
        
        # Print summary
        print("\n📖 Narrative content seeded:")
        for level in db.query(NarrativeLevel).order_by(NarrativeLevel.order_index).all():
            level_fragments = db.query(NarrativeFragment).filter(
                NarrativeFragment.level_id == level.id
            ).all()
            print(f"  - {level.level_key}: {level.title} - {len(level_fragments)} fragmentos")
            
    except Exception as e:
        print(f"❌ Error seeding narrative content: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_narrative()