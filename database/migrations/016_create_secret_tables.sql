-- Migration 016: Create secret tables for hidden fragment discovery
-- This migration adds tables for secret codes and user secret discoveries

-- Create secret_codes table
CREATE TABLE IF NOT EXISTS secret_codes (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL,
    fragment_key VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_secret_codes_code ON secret_codes(code);
CREATE INDEX IF NOT EXISTS idx_secret_codes_fragment_key ON secret_codes(fragment_key);

-- Create user_secret_discoveries table
CREATE TABLE IF NOT EXISTS user_secret_discoveries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    secret_code_id INTEGER REFERENCES secret_codes(id),
    fragment_key VARCHAR(100) NOT NULL,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_secret_discoveries_user_id ON user_secret_discoveries(user_id);
CREATE INDEX IF NOT EXISTS idx_user_secret_discoveries_secret_code_id ON user_secret_discoveries(secret_code_id);
CREATE INDEX IF NOT EXISTS idx_user_secret_discoveries_fragment_key ON user_secret_discoveries(fragment_key);

-- Insert sample secret codes for testing
INSERT INTO secret_codes (code, fragment_key, description, is_active) VALUES
    ('LUCIEN123', 'lucien_backstory', 'Código secreto para el pasado de Lucien', TRUE),
    ('PROPHECY456', 'prophecy_revealed', 'Código secreto para la profecía revelada', TRUE),
    ('CHAMBER789', 'hidden_chamber', 'Código secreto para la cámara oculta', TRUE),
    ('ALTERNATE999', 'alternate_ending', 'Código secreto para el final alternativo', TRUE),
    ('CHARACTER777', 'character_secret', 'Código secreto para el secreto del personaje', TRUE)
ON CONFLICT (code) DO NOTHING;