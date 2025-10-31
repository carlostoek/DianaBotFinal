-- Migration 010: Create channel_posts table for scheduled content publishing

CREATE TABLE IF NOT EXISTS channel_posts (
    id SERIAL PRIMARY KEY,
    channel_id BIGINT NOT NULL,
    post_id BIGINT, -- Nullable for scheduled posts
    post_type VARCHAR(50) NOT NULL, -- 'narrative', 'mission', 'announcement', 'trivia', 'event'
    content TEXT,
    post_metadata JSONB, -- reactions, views, etc.
    scheduled_for TIMESTAMP WITH TIME ZONE, -- When to publish
    published_at TIMESTAMP WITH TIME ZONE, -- When actually published
    status VARCHAR(50) DEFAULT 'draft', -- 'draft', 'scheduled', 'published', 'cancelled'
    recurrence VARCHAR(50), -- 'daily', 'weekly', 'monthly', NULL
    is_protected BOOLEAN DEFAULT FALSE, -- Protect content from forwarding
    linked_mission_id INTEGER REFERENCES missions(id),
    linked_fragment_id INTEGER REFERENCES narrative_fragments(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_channel_posts_channel_id ON channel_posts(channel_id);
CREATE INDEX IF NOT EXISTS idx_channel_posts_status ON channel_posts(status);
CREATE INDEX IF NOT EXISTS idx_channel_posts_scheduled_for ON channel_posts(scheduled_for);
CREATE INDEX IF NOT EXISTS idx_channel_posts_post_type ON channel_posts(post_type);

-- Insert some default scheduled posts for testing
INSERT INTO channel_posts (channel_id, post_type, content, scheduled_for, status, recurrence, is_protected) VALUES
    (-1001234567890, 'announcement', '¡Bienvenidos al canal oficial de DianaBot! 🎉\n\nAquí encontrarás contenido exclusivo, misiones especiales y avances de la historia.', NOW() + INTERVAL '1 hour', 'scheduled', NULL, FALSE),
    (-1001234567890, 'mission', '🚀 Misión del Día: Explora el Bosque Encantado\n\nRecompensa: 50 besitos 💋\n\n¡Acepta la misión para comenzar!', NOW() + INTERVAL '2 hours', 'scheduled', 'daily', FALSE),
    (-1001234567891, 'narrative', '🌙 Fragmento Exclusivo VIP\n\nLucien te susurra al oído: "La luna llena revela secretos que el sol nunca verá..."\n\nContinúa en el siguiente fragmento.', NOW() + INTERVAL '3 hours', 'scheduled', NULL, TRUE);