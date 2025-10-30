#!/usr/bin/env python3
"""
Test script for DianaBot basic functionality
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all imports work correctly"""
    try:
        from bot.main import main
        from bot.handlers.start import start_handler
        from bot.handlers.help import help_handler
        from bot.handlers.stats import stats_handler
        from database.models import User
        from config.settings import settings
        
        print("✅ All imports successful")
        print(f"✅ Bot token configured: {'Yes' if settings.telegram_bot_token else 'No (needs .env file)'}")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False


def test_database_models():
    """Test database model creation"""
    try:
        from database.models import User
        
        # Test User model attributes
        user = User(
            telegram_id=123456789,
            username="test_user",
            first_name="Test",
            last_name="User",
            language_code="es",
            is_bot=False
        )
        
        print("✅ User model creation successful")
        print(f"✅ User attributes: {user.telegram_id}, {user.username}, {user.first_name}")
        
        return True
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing DianaBot Phase 1 Implementation...")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test database models
    if not test_database_models():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All tests passed! Phase 1 implementation is ready.")
        print("\nNext steps:")
        print("1. Create .env file with TELEGRAM_BOT_TOKEN")
        print("2. Run database migrations")
        print("3. Start the bot with: python bot/main.py")
    else:
        print("❌ Some tests failed. Please check the implementation.")