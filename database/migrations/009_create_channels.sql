-- Migration 009: Create channels and channel_posts tables
-- This migration adds support for Telegram channels management

-- Create channels table
CREATE TABLE IF NOT EXISTS channels (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT UNIQUE NOT NULL,
    channel_type VARCHAR(50) NOT NULL, -- 'free', 'vip', 'announcements'
    channel_username VARCHAR(255),
    channel_title VARCHAR(255) NOT NULL,
    settings JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create channel_posts table
CREATE TABLE IF NOT EXISTS channel_posts (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    post_id BIGINT NOT NULL,
    post_type VARCHAR(50) NOT NULL, -- 'welcome', 'announcement', 'content', 'reminder'
    content TEXT,
    post_metadata JSONB,
    posted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_channels_channel_id ON channels(channel_id);
CREATE INDEX IF NOT EXISTS idx_channels_channel_type ON channels(channel_type);
CREATE INDEX IF NOT EXISTS idx_channels_is_active ON channels(is_active);

CREATE INDEX IF NOT EXISTS idx_channel_posts_channel_id ON channel_posts(channel_id);
CREATE INDEX IF NOT EXISTS idx_channel_posts_post_id ON channel_posts(post_id);
CREATE INDEX IF NOT EXISTS idx_channel_posts_post_type ON channel_posts(post_type);

-- Insert default channels configuration
INSERT INTO channels (channel_id, channel_type, channel_title, settings, is_active) VALUES
(-100123456789, 'free', 'DianaBot - Canal Gratuito', '{"welcome_message": "¡Bienvenido al canal gratuito de DianaBot! Aquí encontrarás contenido básico y actualizaciones.", "rules": "Respetar a todos los miembros. No spam."}', TRUE),
(-100987654321, 'vip', 'DianaBot - Canal VIP', '{"welcome_message": "¡Bienvenido al canal VIP de DianaBot! Disfruta de contenido exclusivo y beneficios especiales.", "rules": "Contenido exclusivo para suscriptores VIP. No compartir fuera del canal."}', TRUE),
(-100111111111, 'announcements', 'DianaBot - Anuncios', '{"welcome_message": "Canal oficial de anuncios de DianaBot. Mantente informado sobre nuevas funciones y actualizaciones.", "rules": "Solo anuncios oficiales del equipo."}', TRUE)
ON CONFLICT (channel_id) DO NOTHING;