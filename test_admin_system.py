"""
Test del sistema administrativo con pytest
"""

import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.commands.admin import AdminCommandSystem, ADMIN_USER_IDS


class TestAdminCommandSystem:
    """Test suite para el sistema de comandos administrativos"""
    
    def setup_method(self):
        """Setup para cada test"""
        self.admin_system = AdminCommandSystem()
    
    @pytest.mark.asyncio
    async def test_is_user_admin_with_valid_admin(self):
        """Test que un usuario admin válido es reconocido como admin"""
        # Setup - usar un ID que sabemos está en ADMIN_USER_IDS
        test_admin_id = ADMIN_USER_IDS[0] if ADMIN_USER_IDS else 1280444712
        
        # Test
        result = await self.admin_system.is_user_admin(test_admin_id)
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_is_user_admin_with_non_admin(self):
        """Test que un usuario no admin no es reconocido como admin"""
        # Setup - usar un ID que sabemos NO está en ADMIN_USER_IDS
        non_admin_id = 999999999
        
        # Test
        result = await self.admin_system.is_user_admin(non_admin_id)
        
        # Assert
        assert result is False
    
    def test_admin_menu_methods_exist(self):
        """Test que todos los métodos de menú existen"""
        menu_methods = [
            '_show_main_menu', '_show_vip_menu', '_show_free_menu',
            '_show_gamification_menu', '_show_shop_menu', '_show_narrative_menu',
            '_show_midivan_menu', '_show_stats_menu', '_show_config_menu'
        ]
        
        for method_name in menu_methods:
            assert hasattr(self.admin_system, method_name), f"Método {method_name} no existe"
    
    @pytest.mark.asyncio
    async def test_handle_admin_callback_with_valid_callback(self):
        """Test que handle_admin_callback maneja correctamente un callback válido"""
        # Setup
        mock_update = MagicMock()
        mock_query = AsyncMock()
        mock_query.from_user.id = ADMIN_USER_IDS[0] if ADMIN_USER_IDS else 1280444712
        mock_query.data = "admin_main_menu"
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock()
        
        # Mock the _show_main_menu method
        with patch.object(self.admin_system, '_show_main_menu', new_callable=AsyncMock) as mock_show_menu:
            # Test
            await self.admin_system.handle_admin_callback(mock_update, mock_context)
            
            # Assert
            mock_query.answer.assert_called_once()
            mock_show_menu.assert_called_once_with(mock_query)
    
    @pytest.mark.asyncio
    async def test_handle_admin_callback_with_invalid_callback(self):
        """Test que handle_admin_callback maneja correctamente un callback inválido"""
        # Setup
        mock_update = MagicMock()
        mock_query = AsyncMock()
        mock_query.from_user.id = ADMIN_USER_IDS[0] if ADMIN_USER_IDS else 1280444712
        mock_query.data = "invalid_callback"
        mock_query.message = AsyncMock()
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock()
        
        # Mock the _show_main_menu method
        with patch.object(self.admin_system, '_show_main_menu', new_callable=AsyncMock) as mock_show_menu:
            # Test
            await self.admin_system.handle_admin_callback(mock_update, mock_context)
            
            # Assert
            mock_query.answer.assert_called_once()
            mock_query.edit_message_text.assert_called_once()
            mock_show_menu.assert_called_once_with(mock_query)
    
    @pytest.mark.asyncio
    async def test_handle_admin_callback_with_non_admin_user(self):
        """Test que handle_admin_callback rechaza usuarios no admin"""
        # Setup
        mock_update = MagicMock()
        mock_query = AsyncMock()
        mock_query.from_user.id = 999999999  # Non-admin user
        mock_query.data = "admin_main_menu"
        mock_query.message = AsyncMock()
        mock_update.callback_query = mock_query
        
        mock_context = MagicMock()
        
        # Test
        await self.admin_system.handle_admin_callback(mock_update, mock_context)
        
        # Assert
        mock_query.answer.assert_called_once()
        mock_query.edit_message_text.assert_called_once_with("❌ No tienes permisos de administrador.")


def test_admin_handlers_exist():
    """Test que los handlers principales existen"""
    from bot.commands.admin import admin_command_handler, admin_callback_handler
    
    assert callable(admin_command_handler)
    assert callable(admin_callback_handler)


def test_admin_user_ids_configured():
    """Test que los IDs de admin están configurados"""
    assert len(ADMIN_USER_IDS) > 0, "No hay IDs de administrador configurados"
    assert all(isinstance(user_id, int) for user_id in ADMIN_USER_IDS), "Los IDs de admin deben ser enteros"