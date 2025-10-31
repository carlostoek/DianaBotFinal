"""
Trivia questions seed data for DianaBot
"""

from datetime import datetime
from database.connection import mongo_db


def seed_trivia_questions():
    """Seed trivia questions into MongoDB"""
    
    db = mongo_db
    trivia_collection = db.trivia_questions
    
    # Clear existing trivia questions
    trivia_collection.delete_many({})
    
    trivia_questions = [
        # Lore narrativo - Fácil
        {
            "question_key": "trivia_001",
            "category": "narrative_lore",
            "difficulty": "easy",
            "question": {
                "text": "¿Cuál es el verdadero nombre de Diana antes de su transformación?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Elena", "is_correct": False},
                {"option_id": "b", "text": "Sofía", "is_correct": True},
                {"option_id": "c", "text": "Isabella", "is_correct": False},
                {"option_id": "d", "text": "Desconocido", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 10},
                "incorrect": {"besitos": 2}
            },
            "time_limit_seconds": 30,
            "available_after_fragment": "fragment_005"
        },
        {
            "question_key": "trivia_002",
            "category": "narrative_lore",
            "difficulty": "easy",
            "question": {
                "text": "¿En qué año se construyó la mansión de Lucien?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "1895", "is_correct": False},
                {"option_id": "b", "text": "1923", "is_correct": True},
                {"option_id": "c", "text": "1950", "is_correct": False},
                {"option_id": "d", "text": "1978", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 8},
                "incorrect": {"besitos": 2}
            },
            "time_limit_seconds": 30,
            "available_after_fragment": "fragment_003"
        },
        
        # Detalles de personajes - Medio
        {
            "question_key": "trivia_003",
            "category": "character_details",
            "difficulty": "medium",
            "question": {
                "text": "¿Cuál es el color favorito de Diana?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Rojo", "is_correct": False},
                {"option_id": "b", "text": "Azul", "is_correct": False},
                {"option_id": "c", "text": "Violeta", "is_correct": True},
                {"option_id": "d", "text": "Negro", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 15},
                "incorrect": {"besitos": 3}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": "fragment_008"
        },
        {
            "question_key": "trivia_004",
            "category": "character_details",
            "difficulty": "medium",
            "question": {
                "text": "¿Qué instrumento musical toca Lucien?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Piano", "is_correct": True},
                {"option_id": "b", "text": "Violín", "is_correct": False},
                {"option_id": "c", "text": "Guitarra", "is_correct": False},
                {"option_id": "d", "text": "Flauta", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 12},
                "incorrect": {"besitos": 3}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": "fragment_006"
        },
        
        # Decisiones narrativas - Difícil
        {
            "question_key": "trivia_005",
            "category": "narrative_decisions",
            "difficulty": "hard",
            "question": {
                "text": "¿Qué pasó cuando elegiste confrontar a Lucien en el capítulo 3?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Reveló su verdadera naturaleza", "is_correct": True},
                {"option_id": "b", "text": "Te expulsó de la mansión", "is_correct": False},
                {"option_id": "c", "text": "Se transformó en bestia", "is_correct": False},
                {"option_id": "d", "text": "Nada, ignoró tu confrontación", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 20, "items": [{"item_key": "hint_scroll"}]},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": "fragment_012"
        },
        {
            "question_key": "trivia_006",
            "category": "narrative_decisions",
            "difficulty": "hard",
            "question": {
                "text": "¿Cuál fue la consecuencia de aceptar el pacto con Diana?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Ganaste poderes sobrenaturales", "is_correct": False},
                {"option_id": "b", "text": "Te convertiste en su sirviente eterno", "is_correct": True},
                {"option_id": "c", "text": "Liberaste su alma", "is_correct": False},
                {"option_id": "d", "text": "Destruiste la mansión", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 25, "items": [{"item_key": "ancient_contract"}]},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": "fragment_015"
        },
        
        # Meta-juego - Fácil
        {
            "question_key": "trivia_007",
            "category": "meta_game",
            "difficulty": "easy",
            "question": {
                "text": "¿Cuántos besitos cuesta el item 'Rosa Eterna' en la tienda?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "50", "is_correct": False},
                {"option_id": "b", "text": "100", "is_correct": True},
                {"option_id": "c", "text": "150", "is_correct": False},
                {"option_id": "d", "text": "200", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 8},
                "incorrect": {"besitos": 2}
            },
            "time_limit_seconds": 30,
            "available_after_fragment": None
        },
        {
            "question_key": "trivia_008",
            "category": "meta_game",
            "difficulty": "easy",
            "question": {
                "text": "¿Cuál es la recompensa diaria máxima por completar misiones?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "25 besitos", "is_correct": False},
                {"option_id": "b", "text": "50 besitos", "is_correct": True},
                {"option_id": "c", "text": "75 besitos", "is_correct": False},
                {"option_id": "d", "text": "100 besitos", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 10},
                "incorrect": {"besitos": 2}
            },
            "time_limit_seconds": 30,
            "available_after_fragment": None
        },
        
        # Lore narrativo - Medio
        {
            "question_key": "trivia_009",
            "category": "narrative_lore",
            "difficulty": "medium",
            "question": {
                "text": "¿Por qué Diana está atrapada en la mansión?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Un hechizo ancestral", "is_correct": True},
                {"option_id": "b", "text": "Elección propia", "is_correct": False},
                {"option_id": "c", "text": "Una maldición familiar", "is_correct": False},
                {"option_id": "d", "text": "Está muerta", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 15},
                "incorrect": {"besitos": 3}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": "fragment_010"
        },
        {
            "question_key": "trivia_010",
            "category": "narrative_lore",
            "difficulty": "medium",
            "question": {
                "text": "¿Qué secreto esconde el sótano de la mansión?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Un laboratorio alquímico", "is_correct": False},
                {"option_id": "b", "text": "Una biblioteca prohibida", "is_correct": True},
                {"option_id": "c", "text": "Una cripta familiar", "is_correct": False},
                {"option_id": "d", "text": "Un portal dimensional", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 18},
                "incorrect": {"besitos": 4}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": "fragment_014"
        },
        
        # Detalles de personajes - Difícil
        {
            "question_key": "trivia_011",
            "category": "character_details",
            "difficulty": "hard",
            "question": {
                "text": "¿Cuál es la debilidad secreta de Lucien?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "La luz de luna", "is_correct": False},
                {"option_id": "b", "text": "La plata", "is_correct": True},
                {"option_id": "c", "text": "El agua bendita", "is_correct": False},
                {"option_id": "d", "text": "No tiene debilidades", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 22, "items": [{"item_key": "silver_amulet"}]},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": "fragment_018"
        },
        {
            "question_key": "trivia_012",
            "category": "character_details",
            "difficulty": "hard",
            "question": {
                "text": "¿Qué relación tenía Diana con Lucien antes de su transformación?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Eran hermanos", "is_correct": False},
                {"option_id": "b", "text": "Eran amantes", "is_correct": True},
                {"option_id": "c", "text": "Eran enemigos", "is_correct": False},
                {"option_id": "d", "text": "No se conocían", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 25, "items": [{"item_key": "old_photograph"}]},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": "fragment_020"
        },
        
        # Meta-juego - Medio
        {
            "question_key": "trivia_013",
            "category": "meta_game",
            "difficulty": "medium",
            "question": {
                "text": "¿Cuántos fragmentos narrativos hay en total en la historia principal?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "15", "is_correct": False},
                {"option_id": "b", "text": "20", "is_correct": False},
                {"option_id": "c", "text": "25", "is_correct": True},
                {"option_id": "d", "text": "30", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 12},
                "incorrect": {"besitos": 3}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": None
        },
        {
            "question_key": "trivia_014",
            "category": "meta_game",
            "difficulty": "medium",
            "question": {
                "text": "¿Qué beneficio otorga la suscripción VIP?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Acceso a contenido exclusivo", "is_correct": True},
                {"option_id": "b", "text": "Besitos ilimitados", "is_correct": False},
                {"option_id": "c", "text": "Poderes sobrenaturales", "is_correct": False},
                {"option_id": "d", "text": "Final alternativo", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 15},
                "incorrect": {"besitos": 3}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": None
        },
        
        # Decisiones narrativas - Medio
        {
            "question_key": "trivia_015",
            "category": "narrative_decisions",
            "difficulty": "medium",
            "question": {
                "text": "¿Qué sucede si eliges confiar en Diana desde el principio?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Te revela información crucial", "is_correct": True},
                {"option_id": "b", "text": "Te traiciona", "is_correct": False},
                {"option_id": "c", "text": "Nada cambia", "is_correct": False},
                {"option_id": "d", "text": "Te expulsa de la mansión", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 18},
                "incorrect": {"besitos": 4}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": "fragment_007"
        },
        {
            "question_key": "trivia_016",
            "category": "narrative_decisions",
            "difficulty": "medium",
            "question": {
                "text": "¿Cuál es la consecuencia de investigar el ala oeste prohibida?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Descubres el diario de Diana", "is_correct": True},
                {"option_id": "b", "text": "Te enfrentas a Lucien", "is_correct": False},
                {"option_id": "c", "text": "Encuentras un tesoro", "is_correct": False},
                {"option_id": "d", "text": "Nada importante", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 16},
                "incorrect": {"besitos": 4}
            },
            "time_limit_seconds": 25,
            "available_after_fragment": "fragment_009"
        },
        
        # Lore narrativo - Difícil
        {
            "question_key": "trivia_017",
            "category": "narrative_lore",
            "difficulty": "hard",
            "question": {
                "text": "¿Qué ritual realizó Lucien para mantener a Diana en la mansión?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Un pacto con demonios", "is_correct": False},
                {"option_id": "b", "text": "Un hechizo de sangre ancestral", "is_correct": True},
                {"option_id": "c", "text": "Una ceremonia lunar", "is_correct": False},
                {"option_id": "d", "text": "Un sacrificio humano", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 25, "items": [{"item_key": "ritual_tome"}]},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": "fragment_022"
        },
        {
            "question_key": "trivia_018",
            "category": "narrative_lore",
            "difficulty": "hard",
            "question": {
                "text": "¿Cuál es el verdadero propósito de la mansión?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "Una prisión para almas", "is_correct": True},
                {"option_id": "b", "text": "Un santuario mágico", "is_correct": False},
                {"option_id": "c", "text": "Un laboratorio experimental", "is_correct": False},
                {"option_id": "d", "text": "Una fortaleza militar", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 28, "items": [{"item_key": "soul_key"}]},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": "fragment_025"
        },
        
        # Meta-juego - Difícil
        {
            "question_key": "trivia_019",
            "category": "meta_game",
            "difficulty": "hard",
            "question": {
                "text": "¿Cuál es el achievement más raro de obtener?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "'Maestro del Lore'", "is_correct": False},
                {"option_id": "b", "text": "'Coleccionista Completo'", "is_correct": True},
                {"option_id": "c", "text": "'Rompecorazones'", "is_correct": False},
                {"option_id": "d", "text": "'Explorador Incansable'", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 20},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": None
        },
        {
            "question_key": "trivia_020",
            "category": "meta_game",
            "difficulty": "hard",
            "question": {
                "text": "¿Cuántos finales alternativos existen en la historia?",
                "media_url": None
            },
            "options": [
                {"option_id": "a", "text": "3", "is_correct": False},
                {"option_id": "b", "text": "5", "is_correct": True},
                {"option_id": "c", "text": "7", "is_correct": False},
                {"option_id": "d", "text": "9", "is_correct": False}
            ],
            "rewards": {
                "correct": {"besitos": 22},
                "incorrect": {"besitos": 5}
            },
            "time_limit_seconds": 20,
            "available_after_fragment": None
        }
    ]
    
    # Insert trivia questions
    result = trivia_collection.insert_many(trivia_questions)
    print(f"Inserted {len(result.inserted_ids)} trivia questions")
    
    return result.inserted_ids


if __name__ == "__main__":
    seed_trivia_questions()