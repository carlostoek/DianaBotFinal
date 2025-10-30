#!/usr/bin/env python3
"""
Test script for DianaBot handlers
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, User, Chat, Message
from telegram.ext import ContextTypes
import asyncio

from bot.handlers.start import start_handler
from bot.handlers.help import help_handler
from bot.handlers.stats import stats_handler


async def test_start_handler():
    """Test the start handler"""
    print("🧪 Testing /start handler...")
    
    # Create mock update
    user = User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="es"
    )
    
    chat = Chat(id=123456789, type="private")
    message = Message(
        message_id=1,
        date=None,
        chat=chat,
        from_user=user,
        text="/start"
    )
    
    update = Update(update_id=1, message=message)
    context = ContextTypes.DEFAULT_TYPE
    
    try:
        await start_handler(update, context)
        print("✅ /start handler executed successfully")
        return True
    except Exception as e:
        print(f"❌ /start handler error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_help_handler():
    """Test the help handler"""
    print("🧪 Testing /help handler...")
    
    # Create mock update
    user = User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        last_name="User",
        username="testuser",
        language_code="es"
    )
    
    chat = Chat(id=123456789, type="private")
    message = Message(
        message_id=2,
        date=None,
        chat=chat,
        from_user=user,
        text="/help"
    )
    
    update = Update(update_id=2, message=message)
    context = ContextTypes.DEFAULT_TYPE
    
    try:
        await help_handler(update, context)
        print("✅ /help handler executed successfully")
        return True
    except Exception as e:
        print(f"❌ /help handler error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("🧪 Testing DianaBot Handlers...")
    print("=" * 50)
    
    success = True
    
    # Test handlers
    if not await test_start_handler():
        success = False
    
    if not await test_help_handler():
        success = False
    
    print("=" * 50)
    if success:
        print("🎉 All handler tests passed!")
        print("\nEl bot debería funcionar correctamente ahora.")
    else:
        print("❌ Some handler tests failed.")


if __name__ == "__main__":
    asyncio.run(main())