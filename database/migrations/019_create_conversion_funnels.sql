-- Migration 019: Create conversion funnels table
-- For tracking user conversion journeys (free→VIP, engagement→purchase, etc.)

CREATE TABLE IF NOT EXISTS conversion_funnels (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    funnel_type VARCHAR(50) NOT NULL,
    
    -- Etapas
    stage_entered VARCHAR(50) NOT NULL,
    stage_current VARCHAR(50) NOT NULL,
    stage_completed VARCHAR(50),
    
    -- Fechas
    entered_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    
    -- Estado
    is_active BOOLEAN DEFAULT TRUE,
    is_completed BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    funnel_data JSONB,
    
    -- Índices
    CONSTRAINT fk_conversion_funnels_user FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Índices para optimización
CREATE INDEX IF NOT EXISTS idx_conversion_funnels_user ON conversion_funnels(user_id);
CREATE INDEX IF NOT EXISTS idx_conversion_funnels_type ON conversion_funnels(funnel_type);
CREATE INDEX IF NOT EXISTS idx_conversion_funnels_active ON conversion_funnels(is_active);
CREATE INDEX IF NOT EXISTS idx_conversion_funnels_completed ON conversion_funnels(is_completed);
CREATE INDEX IF NOT EXISTS idx_conversion_funnels_activity ON conversion_funnels(last_activity_at);

-- Comentarios
COMMENT ON TABLE conversion_funnels IS 'Track user conversion journeys through different funnels';
COMMENT ON COLUMN conversion_funnels.funnel_type IS 'Type of conversion funnel: free_to_vip, engagement_to_purchase, free_to_purchaser';
COMMENT ON COLUMN conversion_funnels.stage_entered IS 'Initial stage when user entered the funnel';
COMMENT ON COLUMN conversion_funnels.stage_current IS 'Current stage in the conversion journey';
COMMENT ON COLUMN conversion_funnels.stage_completed IS 'Final stage when conversion completed';
COMMENT ON COLUMN conversion_funnels.funnel_data IS 'JSON metadata with touchpoints, offers shown, barriers, etc.';