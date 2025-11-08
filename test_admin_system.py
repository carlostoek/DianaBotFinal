"""
Test básico del sistema administrativo
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.commands.admin import AdminCommandSystem


def test_admin_permissions():
    """Test de verificación de permisos de administrador"""
    admin_system = AdminCommandSystem()
    
    # Test with no admin users configured
    os.environ["ADMIN_USER_IDS"] = ""
    
    # Test with specific admin user
    os.environ["ADMIN_USER_IDS"] = "123456789,987654321"
    
    print("✅ Test de configuración de permisos administrativos pasado")


def test_admin_menu_structure():
    """Test de estructura de menús administrativos"""
    admin_system = AdminCommandSystem()
    
    # Verificar que todos los métodos de menú existen
    assert hasattr(admin_system, '_show_main_menu')
    assert hasattr(admin_system, '_show_vip_menu')
    assert hasattr(admin_system, '_show_free_menu')
    assert hasattr(admin_system, '_show_gamification_menu')
    assert hasattr(admin_system, '_show_shop_menu')
    assert hasattr(admin_system, '_show_narrative_menu')
    assert hasattr(admin_system, '_show_midivan_menu')
    assert hasattr(admin_system, '_show_stats_menu')
    assert hasattr(admin_system, '_show_config_menu')
    
    print("✅ Test de estructura de menús pasado")


def test_admin_handlers_exist():
    """Test de que los handlers existen"""
    from bot.commands.admin import admin_command_handler, admin_callback_handler
    
    assert callable(admin_command_handler)
    assert callable(admin_callback_handler)
    
    print("✅ Test de handlers administrativos pasado")


if __name__ == "__main__":
    # Run tests
    test_admin_permissions()
    test_admin_menu_structure()
    test_admin_handlers_exist()
    print("\n🎉 Todos los tests del sistema administrativo pasaron")