"""
Trivia keyboards for DianaBot
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Import trivia service inside functions to avoid circular imports
def _get_trivia_service():
    from modules.gamification.trivias import trivia_service
    return trivia_service


def get_trivia_options_keyboard(trivia_id: str) -> InlineKeyboardMarkup:
    """Create keyboard with trivia answer options"""
    
    service = _get_trivia_service()
    trivia = service.get_trivia_by_id(trivia_id)
    if not trivia:
        return InlineKeyboardMarkup([[]])
    
    keyboard = []
    for option in trivia["options"]:
        keyboard.append([
            InlineKeyboardButton(
                f"{option['option_id'].upper()}. {option['text']}",
                callback_data=f"trivia_answer:{trivia_id}:{option['option_id']}"
            )
        ])
    
    return InlineKeyboardMarkup(keyboard)


def get_trivia_categories_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with trivia categories"""
    
    service = _get_trivia_service()
    categories = service.get_categories()
    
    keyboard = []
    for category in categories:
        keyboard.append([
            InlineKeyboardButton(
                category.replace("_", " ").title(),
                callback_data=f"trivia_category:{category}"
            )
        ])
    
    # Add random option
    keyboard.append([
        InlineKeyboardButton(
            "🎲 Trivia Aleatoria",
            callback_data="trivia_category:random"
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_trivia_difficulties_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard with difficulty levels"""
    
    service = _get_trivia_service()
    difficulties = service.get_difficulties()
    
    keyboard = []
    for difficulty in difficulties:
        emoji = {
            "easy": "🟢",
            "medium": "🟡", 
            "hard": "🔴"
        }.get(difficulty, "⚪")
        
        keyboard.append([
            InlineKeyboardButton(
                f"{emoji} {difficulty.title()}",
                callback_data=f"trivia_difficulty:{difficulty}"
            )
        ])
    
    # Add random option
    keyboard.append([
        InlineKeyboardButton(
            "🎲 Dificultad Aleatoria",
            callback_data="trivia_difficulty:random"
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_trivia_stats_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for trivia statistics"""
    
    keyboard = [
        [InlineKeyboardButton("📊 Ver Estadísticas", callback_data="trivia_stats")],
        [InlineKeyboardButton("🎮 Nueva Trivia", callback_data="trivia_new")],
        [InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_trivia_result_keyboard(is_correct: bool, trivia_id: str | None = None) -> InlineKeyboardMarkup:
    """Create keyboard for trivia result"""
    
    if is_correct:
        keyboard = [
            [InlineKeyboardButton("✅ ¡Correcto! Siguiente Trivia", callback_data="trivia_new")],
            [InlineKeyboardButton("📊 Ver Estadísticas", callback_data="trivia_stats")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")]
        ]
    else:
        keyboard = [
            [InlineKeyboardButton("🔄 Intentar Otra", callback_data="trivia_new")],
            [InlineKeyboardButton("📊 Ver Estadísticas", callback_data="trivia_stats")],
            [InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")]
        ]
    
    return InlineKeyboardMarkup(keyboard)


def get_trivia_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard for trivia"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Trivia Aleatoria", callback_data="trivia_new")],
        [InlineKeyboardButton("📚 Elegir Categoría", callback_data="trivia_categories")],
        [InlineKeyboardButton("⚡ Elegir Dificultad", callback_data="trivia_difficulties")],
        [InlineKeyboardButton("📊 Mis Estadísticas", callback_data="trivia_stats")],
        [InlineKeyboardButton("🏠 Menú Principal", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)