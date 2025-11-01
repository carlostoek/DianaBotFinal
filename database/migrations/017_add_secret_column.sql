-- Add is_secret column to narrative_fragments table
ALTER TABLE narrative_fragments ADD COLUMN is_secret BOOLEAN DEFAULT FALSE;

-- Add any secret codes that should exist
INSERT INTO secret_codes (code, fragment_key, description, is_active, created_at) VALUES
('LUCIEN123', 'lucien_backstory', 'Descubre el pasado oculto de Lucien', TRUE, NOW()),
('PROPHECY456', 'prophecy_revealed', 'Revela la profecía completa', TRUE, NOW()),
('CHAMBER789', 'hidden_chamber', 'Accede a la cámara secreta', TRUE, NOW()),
('ALTERNATE321', 'alternate_ending', 'Desbloquea el final alternativo', TRUE, NOW()),
('CHARACTER654', 'character_secret', 'Conoce el secreto del personaje', TRUE, NOW());