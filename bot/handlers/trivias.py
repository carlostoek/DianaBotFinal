"""
Trivia handlers for DianaBot
"""

import time
import logging
from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CallbackQueryHandler
from telegram.error import BadRequest

from modules.gamification.trivias import trivia_service
from bot.keyboards.trivia_keyboards import (
    get_trivia_options_keyboard,
    get_trivia_categories_keyboard,
    get_trivia_difficulties_keyboard,
    get_trivia_stats_keyboard,
    get_trivia_result_keyboard,
    get_trivia_main_menu_keyboard
)

logger = logging.getLogger(__name__)


async def trivia_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start trivia interaction"""
    user_id = update.effective_user.id
    
    await update.message.reply_text(
        "🎮 *Sistema de Trivias DianaBot*\n\n"
        "Pon a prueba tu conocimiento sobre el lore de Diana y gana recompensas.\n\n"
        "*Características:*\n"
        "• Preguntas sobre lore narrativo\n"
        "• Recompensas por respuestas correctas\n"
        "• Estadísticas detalladas\n"
        "• Diferentes categorías y dificultades\n\n"
        "¡Elige una opción para comenzar!",
        reply_markup=get_trivia_main_menu_keyboard(),
        parse_mode="Markdown"
    )


async def trivia_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start a new random trivia"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    
    # Get random trivia
    trivia = trivia_service.get_random_trivia()
    
    if not trivia:
        await query.edit_message_text(
            "❌ No hay trivias disponibles en este momento.\n"
            "Intenta más tarde o contacta con un administrador.",
            reply_markup=get_trivia_main_menu_keyboard()
        )
        return
    
    # Store trivia start time in context
    context.user_data[f"trivia_start_{trivia['_id']}"] = time.time()
    
    # Format question text
    question_text = (
        f"🧠 *Trivia* - {trivia['category'].replace('_', ' ').title()}\n"
        f"📊 Dificultad: {trivia['difficulty'].title()}\n"
        f"⏱️ Tiempo: {trivia['time_limit_seconds']} segundos\n\n"
        f"*{trivia['question']['text']}*\n\n"
        "*Opciones:*"
    )
    
    await query.edit_message_text(
        question_text,
        reply_markup=get_trivia_options_keyboard(trivia["_id"]),
        parse_mode="Markdown"
    )


async def trivia_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle trivia answer"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    data = query.data.split(":")
    
    if len(data) != 3:
        await query.edit_message_text(
            "❌ Error procesando respuesta. Intenta nuevamente.",
            reply_markup=get_trivia_main_menu_keyboard()
        )
        return
    
    trivia_id = data[1]
    answer = data[2]
    
    # Calculate response time
    start_time = context.user_data.get(f"trivia_start_{trivia_id}")
    if not start_time:
        response_time = 30.0  # Default if start time not found
    else:
        response_time = time.time() - start_time
    
    # Submit answer
    result = trivia_service.submit_answer(user_id, trivia_id, answer, response_time)
    
    if not result["success"]:
        await query.edit_message_text(
            f"❌ Error: {result['error']}",
            reply_markup=get_trivia_main_menu_keyboard()
        )
        return
    
    # Format result message
    if result["correct"]:
        result_text = (
            f"✅ *¡Correcto!*\n\n"
            f"🎯 Respuesta correcta: *{result['correct_answer'].upper()}*\n"
            f"⏱️ Tiempo de respuesta: *{result['response_time']:.1f}s*\n"
            f"💰 Recompensa: *{result['rewards'].get('besitos', 0)} besitos*"
        )
        
        if result['rewards'].get('speed_bonus'):
            result_text += "\n⚡ *¡Bonus por velocidad!*"
        
        if result['rewards'].get('items'):
            items_text = ", ".join([item['item_key'] for item in result['rewards']['items']])
            result_text += f"\n🎁 Items obtenidos: *{items_text}*"
    else:
        result_text = (
            f"❌ *Incorrecto*\n\n"
            f"🎯 Respuesta correcta: *{result['correct_answer'].upper()}*\n"
            f"⏱️ Tiempo de respuesta: *{result['response_time']:.1f}s*\n"
            f"💰 Recompensa: *{result['rewards'].get('besitos', 0)} besitos*"
        )
    
    await query.edit_message_text(
        result_text,
        reply_markup=get_trivia_result_keyboard(result["correct"], trivia_id),
        parse_mode="Markdown"
    )


async def trivia_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trivia categories"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "📚 *Categorías de Trivias*\n\n"
        "Elige una categoría para jugar trivias específicas sobre el lore de Diana:",
        reply_markup=get_trivia_categories_keyboard(),
        parse_mode="Markdown"
    )


async def trivia_category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle category selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    category = data[1] if len(data) > 1 else "random"
    
    if category == "random":
        await trivia_new(update, context)
        return
    
    user_id = update.effective_user.id
    
    # Get trivia from selected category
    trivia = trivia_service.get_random_trivia(category=category)
    
    if not trivia:
        await query.edit_message_text(
            f"❌ No hay trivias disponibles en la categoría '{category}'.\n"
            "Intenta con otra categoría o elige trivias aleatorias.",
            reply_markup=get_trivia_main_menu_keyboard()
        )
        return
    
    # Store trivia start time in context
    context.user_data[f"trivia_start_{trivia['_id']}"] = time.time()
    
    # Format question text
    question_text = (
        f"🧠 *Trivia* - {trivia['category'].replace('_', ' ').title()}\n"
        f"📊 Dificultad: {trivia['difficulty'].title()}\n"
        f"⏱️ Tiempo: {trivia['time_limit_seconds']} segundos\n\n"
        f"*{trivia['question']['text']}*\n\n"
        "*Opciones:*"
    )
    
    await query.edit_message_text(
        question_text,
        reply_markup=get_trivia_options_keyboard(trivia["_id"]),
        parse_mode="Markdown"
    )


async def trivia_difficulties(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trivia difficulty levels"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "⚡ *Niveles de Dificultad*\n\n"
        "Elige un nivel de dificultad para las trivias:\n\n"
        "🟢 *Fácil*: Preguntas básicas, recompensas menores\n"
        "🟡 *Medio*: Preguntas intermedias, recompensas moderadas\n"
        "🔴 *Difícil*: Preguntas avanzadas, recompensas mayores",
        reply_markup=get_trivia_difficulties_keyboard(),
        parse_mode="Markdown"
    )


async def trivia_difficulty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle difficulty selection"""
    query = update.callback_query
    await query.answer()
    
    data = query.data.split(":")
    difficulty = data[1] if len(data) > 1 else "random"
    
    if difficulty == "random":
        await trivia_new(update, context)
        return
    
    user_id = update.effective_user.id
    
    # Get trivia with selected difficulty
    trivia = trivia_service.get_random_trivia(difficulty=difficulty)
    
    if not trivia:
        await query.edit_message_text(
            f"❌ No hay trivias disponibles en dificultad '{difficulty}'.\n"
            "Intenta con otra dificultad o elige trivias aleatorias.",
            reply_markup=get_trivia_main_menu_keyboard()
        )
        return
    
    # Store trivia start time in context
    context.user_data[f"trivia_start_{trivia['_id']}"] = time.time()
    
    # Format question text
    question_text = (
        f"🧠 *Trivia* - {trivia['category'].replace('_', ' ').title()}\n"
        f"📊 Dificultad: {trivia['difficulty'].title()}\n"
        f"⏱️ Tiempo: {trivia['time_limit_seconds']} segundos\n\n"
        f"*{trivia['question']['text']}*\n\n"
        "*Opciones:*"
    )
    
    await query.edit_message_text(
        question_text,
        reply_markup=get_trivia_options_keyboard(trivia["_id"]),
        parse_mode="Markdown"
    )


async def trivia_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show trivia statistics"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    stats = trivia_service.get_trivia_stats(user_id)
    
    stats_text = (
        f"📊 *Estadísticas de Trivias*\n\n"
        f"🎯 Total respondidas: *{stats['total_answered']}*\n"
        f"✅ Correctas: *{stats['correct_answers']}*\n"
        f"❌ Incorrectas: *{stats['incorrect_answers']}*\n"
        f"🎯 Precisión: *{stats['accuracy']:.1f}%*\n"
        f"⏱️ Tiempo promedio: *{stats['average_response_time']:.1f}s*\n"
        f"💰 Besitos ganados: *{stats['total_besitos_earned']}*\n\n"
    )
    
    # Add category stats
    if stats['category_stats']:
        stats_text += "*Por Categoría:*\n"
        for category, cat_stats in stats['category_stats'].items():
            accuracy = (cat_stats['correct'] / cat_stats['answered'] * 100) if cat_stats['answered'] > 0 else 0
            stats_text += f"• {category.replace('_', ' ').title()}: {cat_stats['correct']}/{cat_stats['answered']} ({accuracy:.1f}%)\n"
    
    stats_text += "\n"
    
    # Add difficulty stats
    if stats['difficulty_stats']:
        stats_text += "*Por Dificultad:*\n"
        for difficulty, diff_stats in stats['difficulty_stats'].items():
            accuracy = (diff_stats['correct'] / diff_stats['answered'] * 100) if diff_stats['answered'] > 0 else 0
            stats_text += f"• {difficulty.title()}: {diff_stats['correct']}/{diff_stats['answered']} ({accuracy:.1f}%)\n"
    
    await query.edit_message_text(
        stats_text,
        reply_markup=get_trivia_stats_keyboard(),
        parse_mode="Markdown"
    )


async def trivia_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to trivia main menu"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "🎮 *Sistema de Trivias DianaBot*\n\n"
        "Pon a prueba tu conocimiento sobre el lore de Diana y gana recompensas.\n\n"
        "*Características:*\n"
        "• Preguntas sobre lore narrativo\n"
        "• Recompensas por respuestas correctas\n"
        "• Estadísticas detalladas\n"
        "• Diferentes categorías y dificultades\n\n"
        "¡Elige una opción para comenzar!",
        reply_markup=get_trivia_main_menu_keyboard(),
        parse_mode="Markdown"
    )


# Handler registration
def register_trivia_handlers(application):
    """Register all trivia handlers"""
    
    application.add_handler(CallbackQueryHandler(trivia_new, pattern="^trivia_new$"))
    application.add_handler(CallbackQueryHandler(trivia_categories, pattern="^trivia_categories$"))
    application.add_handler(CallbackQueryHandler(trivia_difficulties, pattern="^trivia_difficulties$"))
    application.add_handler(CallbackQueryHandler(trivia_stats, pattern="^trivia_stats$"))
    application.add_handler(CallbackQueryHandler(trivia_main_menu, pattern="^trivia_main_menu$"))
    
    application.add_handler(CallbackQueryHandler(trivia_category_selected, pattern="^trivia_category:"))
    application.add_handler(CallbackQueryHandler(trivia_difficulty_selected, pattern="^trivia_difficulty:"))
    application.add_handler(CallbackQueryHandler(trivia_answer, pattern="^trivia_answer:"))
    
    logger.info("Trivia handlers registered successfully")