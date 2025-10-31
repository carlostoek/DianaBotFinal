-- Migration 005: Create missions tables
-- Date: 2025-10-31
-- Description: Add missions and user_missions tables for gamification system

-- Missions table
CREATE TABLE missions (
    id SERIAL PRIMARY KEY,
    mission_key VARCHAR(100) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    mission_type VARCHAR(50) NOT NULL, -- 'daily', 'weekly', 'narrative', 'special'
    recurrence VARCHAR(50) NOT NULL, -- 'once', 'daily', 'weekly'
    requirements JSONB NOT NULL, -- qué debe hacer el usuario
    rewards JSONB NOT NULL, -- besitos, items, achievements
    expiry_date TIMESTAMP WITH TIME ZONE, -- para misiones temporales
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User missions progress tracking
CREATE TABLE user_missions (
    user_id INTEGER REFERENCES users(id),
    mission_id INTEGER REFERENCES missions(id),
    status VARCHAR(50) NOT NULL, -- 'active', 'completed', 'expired'
    progress JSONB, -- progreso actual hacia requisitos
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY (user_id, mission_id)
);

-- Create indexes for performance
CREATE INDEX idx_missions_mission_key ON missions(mission_key);
CREATE INDEX idx_missions_type ON missions(mission_type);
CREATE INDEX idx_missions_active ON missions(is_active);
CREATE INDEX idx_user_missions_user_id ON user_missions(user_id);
CREATE INDEX idx_user_missions_status ON user_missions(status);
CREATE INDEX idx_user_missions_assigned_at ON user_missions(assigned_at);

-- Insert initial missions
INSERT INTO missions (mission_key, title, description, mission_type, recurrence, requirements, rewards) VALUES
    -- Daily missions
    ('daily_complete_fragment', 'Explorador Diario', 'Completa 1 fragmento narrativo', 'daily', 'daily', 
     '{"fragments_completed": 1}', 
     '{"besitos": 20}'),
    
    ('daily_claim_reward', 'Recompensa Diaria', 'Reclama tu regalo diario', 'daily', 'daily', 
     '{"daily_reward_claimed": 1}', 
     '{"besitos": 10}'),
    
    -- Weekly missions
    ('weekly_complete_fragments', 'Aventurero Semanal', 'Completa 5 fragmentos esta semana', 'weekly', 'weekly', 
     '{"fragments_completed": 5}', 
     '{"besitos": 100}'),
    
    -- Narrative missions
    ('narrative_reach_level_2', 'Ascenso Narrativo', 'Alcanza el nivel 2 en la narrativa', 'narrative', 'once', 
     '{"narrative_level": 2}', 
     '{"besitos": 50, "items": ["key_mansion_garden"]}');

-- Create indexes for the inserted missions
CREATE INDEX idx_missions_daily ON missions(mission_type) WHERE mission_type = 'daily';
CREATE INDEX idx_missions_weekly ON missions(mission_type) WHERE mission_type = 'weekly';
CREATE INDEX idx_missions_narrative ON missions(mission_type) WHERE mission_type = 'narrative';