-- Migration: Create users table
-- This migration creates the users table for storing Telegram user information

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username VARCHAR(255),
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255),
    language_code VARCHAR(10),
    is_premium BOOLEAN DEFAULT FALSE,
    is_bot BOOLEAN DEFAULT FALSE,
    
    -- User state and progress
    current_state VARCHAR(50) DEFAULT 'start',
    current_story VARCHAR(50),
    current_chapter VARCHAR(50),
    
    -- Stats
    total_messages INTEGER DEFAULT 0,
    total_commands INTEGER DEFAULT 0,
    total_stories_started INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_current_state ON users(current_state);
CREATE INDEX IF NOT EXISTS idx_users_last_active ON users(last_active);