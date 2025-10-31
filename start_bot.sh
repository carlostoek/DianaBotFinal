#!/bin/bash

# DianaBot Startup Script
cd "$(dirname "$0")"

# Activate virtual environment if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Function to check if a service is running
check_service() {
    local service_name=$1
    local display_name=$2
    
    if systemctl is-active --quiet "$service_name"; then
        echo "✅ $display_name is already running"
        return 0
    else
        echo "⚠️  $display_name is not running, attempting to start..."
        if sudo systemctl start "$service_name"; then
            echo "✅ $display_name started successfully"
            return 0
        else
            echo "❌ Failed to start $display_name"
            return 1
        fi
    fi
}

# Function to check if a port is listening
check_port() {
    local port=$1
    local service_name=$2
    
    if netstat -tuln | grep ":$port " > /dev/null; then
        echo "✅ $service_name is listening on port $port"
        return 0
    else
        echo "❌ $service_name is not listening on port $port"
        return 1
    fi
}

echo "🔧 Checking required services..."

# Check PostgreSQL (using port check since systemd service shows active but may not be listening)
if check_port 5432 "PostgreSQL"; then
    echo "✅ PostgreSQL is ready"
else
    echo "⚠️  PostgreSQL may need manual setup"
fi

# Check and start MongoDB
if check_service "mongod" "MongoDB"; then
    # Wait a moment for MongoDB to fully start
    sleep 2
    if check_port 27017 "MongoDB"; then
        echo "✅ MongoDB is ready"
    else
        echo "⚠️  MongoDB started but not listening on port 27017"
    fi
else
    echo "❌ MongoDB failed to start, bot may not work correctly"
fi

# Check Redis (optional, but good to have)
if check_port 6379 "Redis"; then
    echo "✅ Redis is ready"
else
    echo "⚠️  Redis is not running (optional for basic functionality)"
fi

echo ""
echo "🤖 Starting DianaBot..."
python bot/main.py