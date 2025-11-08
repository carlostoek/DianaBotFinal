"""
Sistema de Comandos Administrativos - DianaBot

Módulo principal para el comando /admin y todos los sub-menús administrativos
"""

import logging
from typing import Dict, Any, Optional
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackContext
from config.settings import settings

logger = logging.getLogger(__name__)

# Get admin user IDs from settings (comma-separated)
ADMIN_USER_IDS = [int(id.strip()) for id in settings.admin_user_ids.split(",") if id.strip()]


class AdminCommandSystem:
    """
    Sistema central de comandos administrativos
    Maneja el comando /admin y todos los sub-menús
    """
    
    def __init__(self):
        # No database dependency for now - using simple admin ID list
        pass
    
    async def is_user_admin(self, user_id: int) -> bool:
        """Verifica si el usuario tiene permisos de administrador"""
        # Simple check against hardcoded admin IDs from environment
        return user_id in ADMIN_USER_IDS
    
    async def show_admin_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Muestra el menú principal de administración"""
        if not update.message or not update.effective_user:
            return
            
        user_id = update.effective_user.id
        
        # Verificar permisos
        if not await self.is_user_admin(user_id):
            await update.message.reply_text(
                "❌ No tienes permisos de administrador para acceder a esta función."
            )
            return
        
        # Crear teclado inline para el menú principal
        keyboard = [
            [
                InlineKeyboardButton("💎 Canal VIP", callback_data="admin_vip"),
                InlineKeyboardButton("💬 Canal Free", callback_data="admin_free")
            ],
            [
                InlineKeyboardButton("🎮 Juego Kinky", callback_data="admin_kinky_game"),
                InlineKeyboardButton("🛒 Tienda", callback_data="admin_shop")
            ],
            [
                InlineKeyboardButton("📖 Narrativa", callback_data="admin_narrative_panel"),
                InlineKeyboardButton("💎 Mi Diván", callback_data="admin_midivan")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="admin_stats"),
                InlineKeyboardButton("⚙️ Configuración", callback_data="admin_config")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_main_menu"),
                InlineKeyboardButton("↩️ Volver", callback_data="admin_back")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 **Panel de Administración - DianaBot**\n\n"
            "Selecciona una opción para gestionar:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_admin_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Maneja las llamadas de retorno de los botones del menú administrativo"""
        if not update.callback_query:
            return
            
        query = update.callback_query
        await query.answer()
        
        if not query.from_user:
            return
            
        user_id = query.from_user.id
        callback_data = query.data
        
        # Verificar permisos
        if not await self.is_user_admin(user_id):
            if query.message:
                await query.edit_message_text(
                    "❌ No tienes permisos de administrador."
                )
            return
        
        # Dispatch dictionary for callback handlers
        callback_handlers = {
            "admin_main_menu": self._show_main_menu,
            "admin_back": self._show_main_menu,  # Simple back to main menu for now
            "admin_vip": self._show_vip_menu,
            "admin_free": self._show_free_menu,
            "admin_kinky_game": self._show_gamification_menu,
            "admin_shop": self._show_shop_menu,
            "admin_narrative_panel": self._show_narrative_menu,
            "admin_midivan": self._show_midivan_menu,
            "admin_stats": self._show_stats_menu,
            "admin_config": self._show_config_menu
        }
        
        # Handle callback using dispatch dictionary
        handler = callback_handlers.get(callback_data or "")
        if handler:
            await handler(query)
        else:
            if query.message:
                await query.edit_message_text(
                    "❌ Opción no reconocida. Volviendo al menú principal."
                )
                await self._show_main_menu(query)
    
    async def _show_main_menu(self, query):
        """Muestra el menú principal"""
        keyboard = [
            [
                InlineKeyboardButton("💎 Canal VIP", callback_data="admin_vip"),
                InlineKeyboardButton("💬 Canal Free", callback_data="admin_free")
            ],
            [
                InlineKeyboardButton("🎮 Juego Kinky", callback_data="admin_kinky_game"),
                InlineKeyboardButton("🛒 Tienda", callback_data="admin_shop")
            ],
            [
                InlineKeyboardButton("📖 Narrativa", callback_data="admin_narrative_panel"),
                InlineKeyboardButton("💎 Mi Diván", callback_data="admin_midivan")
            ],
            [
                InlineKeyboardButton("📊 Estadísticas", callback_data="admin_stats"),
                InlineKeyboardButton("⚙️ Configuración", callback_data="admin_config")
            ],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🔧 **Panel de Administración - DianaBot**\n\n"
            "Selecciona una opción para gestionar:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_vip_menu(self, query):
        """Muestra el menú de gestión del canal VIP"""
        keyboard = [
            [InlineKeyboardButton("📊 Estadísticas", callback_data="vip_stats")],
            [InlineKeyboardButton("🔑 Generar Token", callback_data="vip_generate_token")],
            [InlineKeyboardButton("👥 Suscriptores", callback_data="vip_manage")],
            [InlineKeyboardButton("🏅 Asignar Insignia", callback_data="vip_manual_badge")],
            [InlineKeyboardButton("📝 Publicar Canal", callback_data="admin_send_channel_post")],
            [InlineKeyboardButton("⚙️ Configuración", callback_data="vip_config")],
            [InlineKeyboardButton("💋 Config Reacciones", callback_data="vip_config_reactions")],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_vip_channel"),
                InlineKeyboardButton("↩️ Volver", callback_data="admin_main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💎 **Gestión del Canal VIP**\n\n"
            "Opciones de administración para el canal de suscriptores VIP:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_free_menu(self, query):
        """Muestra el menú de gestión del canal Free"""
        keyboard = [
            [InlineKeyboardButton("⚙️ Configurar Canal", callback_data="configure_free_channel")],
            [InlineKeyboardButton("⏰ Tiempo Espera", callback_data="set_wait_time")],
            [InlineKeyboardButton("🔗 Crear Enlace", callback_data="create_invite_link")],
            [InlineKeyboardButton("📝 Enviar Contenido", callback_data="send_to_free_channel")],
            [InlineKeyboardButton("⚡ Procesar Ahora", callback_data="process_pending_now")],
            [InlineKeyboardButton("🧹 Limpiar Antiguas", callback_data="cleanup_old_requests")],
            [InlineKeyboardButton("📊 Estadísticas", callback_data="free_channel_stats")],
            [InlineKeyboardButton("💋 Config Reacciones", callback_data="free_config_reactions")],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_free_channel"),
                InlineKeyboardButton("↩️ Volver", callback_data="admin_main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💬 **Gestión del Canal Free**\n\n"
            "Opciones de administración para el canal gratuito:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_gamification_menu(self, query):
        """Muestra el menú de gamificación (Juego Kinky)"""
        keyboard = [
            [InlineKeyboardButton("👥 Usuarios", callback_data="admin_manage_users")],
            [InlineKeyboardButton("🎯 Misiones", callback_data="admin_content_missions")],
            [InlineKeyboardButton("🏅 Insignias", callback_data="admin_content_badges")],
            [InlineKeyboardButton("📈 Niveles", callback_data="admin_content_levels")],
            [InlineKeyboardButton("🎁 Catálogo VIP", callback_data="admin_content_rewards")],
            [InlineKeyboardButton("🏛️ Subastas", callback_data="admin_auction_main")],
            [InlineKeyboardButton("🎁 Regalos Diarios", callback_data="admin_content_daily_gifts")],
            [InlineKeyboardButton("🕹 Minijuegos", callback_data="admin_content_minigames")],
            [InlineKeyboardButton("🗺️ Pistas", callback_data="admin_content_lore_pieces")],
            [InlineKeyboardButton("🎉 Eventos", callback_data="admin_manage_events_sorteos")],
            [InlineKeyboardButton("📦 CMS Journey", callback_data="cms_main")],
            [
                InlineKeyboardButton("🔄 Actualizar", callback_data="admin_manage_content"),
                InlineKeyboardButton("🏠 Panel Admin", callback_data="admin_main_menu")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🎮 **Panel de Gamificación - Juego Kinky**\n\n"
            "Gestión completa de todos los aspectos de ludificación:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_shop_menu(self, query):
        """Muestra el menú de gestión de la tienda"""
        keyboard = [
            [InlineKeyboardButton("📦 Ver Productos", callback_data="admin_shop_list")],
            [InlineKeyboardButton("➕ Crear Producto", callback_data="admin_shop_create")],
            [InlineKeyboardButton("🔗 Gestionar Desbloqueos", callback_data="admin_shop_unlocks")],
            [InlineKeyboardButton("📊 Reportes de Ventas", callback_data="admin_shop_reports")],
            [InlineKeyboardButton("🔙 Volver", callback_data="admin_main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🛒 **Gestión de la Tienda**\n\n"
            "Administración completa de productos y ventas:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_narrative_menu(self, query):
        """Muestra el menú del panel de narrativa"""
        keyboard = [
            [InlineKeyboardButton("📖 Gestionar Fragmentos", callback_data="narrative_manage_fragments")],
            [InlineKeyboardButton("🌳 Editar Árbol de Decisiones", callback_data="narrative_edit_tree")],
            [InlineKeyboardButton("🔍 Validar Contenido", callback_data="narrative_validate")],
            [InlineKeyboardButton("📤 Publicar Cambios", callback_data="narrative_publish")],
            [InlineKeyboardButton("🔙 Volver", callback_data="admin_main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📖 **Panel de Narrativa**\n\n"
            "Gestión de la historia interactiva del bot:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_midivan_menu(self, query):
        """Muestra el menú de Mi Diván"""
        keyboard = [
            [InlineKeyboardButton("📬 Ver Mensajes", callback_data="midivan_view_messages")],
            [InlineKeyboardButton("📊 Estadísticas de Mensajes", callback_data="midivan_message_stats")],
            [InlineKeyboardButton("💘 Gestionar Quizzes", callback_data="midivan_manage_quizzes")],
            [InlineKeyboardButton("📈 Estadísticas de Quizzes", callback_data="midivan_quiz_stats")],
            [InlineKeyboardButton("🔙 Volver", callback_data="admin_main_menu")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "💎 **Mi Diván**\n\n"
            "Gestión de mensajes anónimos y quizzes:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def _show_stats_menu(self, query):
        """Muestra el menú de estadísticas"""
        await query.edit_message_text(
            "📊 **Estadísticas del Bot**\n\n"
            "*Funcionalidad en desarrollo*\n\n"
            "Próximamente mostrará:\n"
            "• Número total de usuarios\n"
            "• Suscripciones activas/vencidas\n"
            "• Ingresos totales\n"
            "• Estado de configuración",
            parse_mode='Markdown'
        )
    
    async def _show_config_menu(self, query):
        """Muestra el menú de configuración"""
        await query.edit_message_text(
            "⚙️ **Configuración del Bot**\n\n"
            "*Funcionalidad en desarrollo*\n\n"
            "Próximamente mostrará el estado de:\n"
            "• Configuración de canales\n"
            "• Tarifas configuradas\n"
            "• Gamificación activa",
            parse_mode='Markdown'
        )


# Instancia global del sistema de comandos administrativos
admin_system = AdminCommandSystem()


async def admin_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador principal del comando /admin"""
    await admin_system.show_admin_menu(update, context)


async def admin_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Manejador de callbacks del menú administrativo"""
    await admin_system.handle_admin_callback(update, context)