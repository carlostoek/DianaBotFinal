"""
Interactive keyboards for narrative system
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_level_selection_keyboard(levels):
    """Create keyboard for level selection"""
    keyboard = []
    
    for level in levels:
        callback_data = f"narrative:start:{level.level_key}"
        button_text = f"📖 {level.title}"
        
        # Add VIP indicator if applicable (placeholder for future VIP system)
        # if hasattr(level, 'is_vip') and level.is_vip:
        #     button_text += " 🔒"
        
        keyboard.append([
            InlineKeyboardButton(button_text, callback_data=callback_data)
        ])
    
    # Add back button
    keyboard.append([
        InlineKeyboardButton("🔙 Volver", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_decision_keyboard(fragment_key: str, decisions: list):
    """Create keyboard for narrative decisions"""
    keyboard = []
    
    for decision in decisions:
        callback_data = f"narrative:decision:{fragment_key}:{decision['decision_id']}"
        keyboard.append([
            InlineKeyboardButton(decision["text"], callback_data=callback_data)
        ])
    
    # Add continue and back buttons
    keyboard.append([
        InlineKeyboardButton("⏭️ Continuar", callback_data="narrative:continue"),
        InlineKeyboardButton("🔙 Menú", callback_data="main_menu")
    ])
    
    return InlineKeyboardMarkup(keyboard)


def get_navigation_keyboard():
    """Create navigation keyboard for narrative system"""
    keyboard = [
        [
            InlineKeyboardButton("📖 Continuar Historia", callback_data="narrative:continue"),
            InlineKeyboardButton("🎯 Nuevas Historias", callback_data="narrative:levels")
        ],
        [
            InlineKeyboardButton("📊 Progreso", callback_data="narrative:progress"),
            InlineKeyboardButton("🔙 Menú Principal", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_story_completion_keyboard():
    """Create keyboard for when a story is completed"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Nueva Historia", callback_data="narrative:levels"),
            InlineKeyboardButton("📊 Ver Progreso", callback_data="narrative:progress")
        ],
        [
            InlineKeyboardButton("🔙 Menú Principal", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)


def get_quick_actions_keyboard():
    """Create quick actions keyboard for narrative system"""
    keyboard = [
        [
            InlineKeyboardButton("⏭️ Continuar", callback_data="narrative:continue"),
            InlineKeyboardButton("📖 Nueva", callback_data="narrative:levels")
        ],
        [
            InlineKeyboardButton("💾 Guardar", callback_data="narrative:save"),
            InlineKeyboardButton("📊 Estadísticas", callback_data="narrative:stats")
        ],
        [
            InlineKeyboardButton("🔙 Menú", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(keyboard)