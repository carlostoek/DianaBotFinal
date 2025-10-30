#!/bin/bash

# DianaBot Startup Script
cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the bot
echo "🤖 Starting DianaBot..."
python bot/main.py