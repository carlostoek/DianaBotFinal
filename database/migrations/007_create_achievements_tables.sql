-- Migration 007: Create achievements tables
-- Date: 2025-10-31
-- Description: Add achievements and user_achievements tables for gamification system

-- Achievements table
CREATE TABLE achievements (
    id SERIAL PRIMARY KEY,
    achievement_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    icon_emoji VARCHAR(50),
    points INTEGER DEFAULT 0,
    reward_besitos INTEGER DEFAULT 0,
    reward_item_id INTEGER REFERENCES items(id),
    unlock_conditions JSONB NOT NULL, -- criterios para desbloquear
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User achievements progress tracking
CREATE TABLE user_achievements (
    user_id INTEGER REFERENCES users(id),
    achievement_id INTEGER REFERENCES achievements(id),
    unlocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    progress JSONB, -- para logros progresivos
    PRIMARY KEY (user_id, achievement_id)
);

-- Create indexes for performance
CREATE INDEX idx_achievements_achievement_key ON achievements(achievement_key);
CREATE INDEX idx_achievements_points ON achievements(points);
CREATE INDEX idx_user_achievements_user_id ON user_achievements(user_id);
CREATE INDEX idx_user_achievements_unlocked_at ON user_achievements(unlocked_at);

-- Insert initial achievements
INSERT INTO achievements (achievement_key, name, description, icon_emoji, points, reward_besitos, unlock_conditions) VALUES
    -- Progreso Narrativo
    ('first_decision', 'Primera Decisión', 'Completa tu primer fragmento con decisión', '🎯', 10, 25, 
     '{"fragments_completed": 1}'),
    
    ('novice_collector', 'Coleccionista Novato', 'Posee 5 items en tu inventario', '📦', 15, 50, 
     '{"items_owned": 5}'),
    
    ('millionaire', 'Millonario', 'Acumula 1000 besitos lifetime', '💰', 20, 100, 
     '{"lifetime_besitos": 1000}'),
    
    ('dedicated', 'Dedicado', 'Completa 5 misiones diarias', '🏆', 25, 75, 
     '{"daily_missions_completed": 5}'),
    
    ('explorer', 'Explorador', 'Completa nivel 1 de la narrativa', '🗺️', 30, 150, 
     '{"narrative_level": 1}');

-- Create indexes for the inserted achievements
CREATE INDEX idx_achievements_narrative ON achievements(achievement_key) WHERE achievement_key LIKE '%narrative%';
CREATE INDEX idx_achievements_economic ON achievements(achievement_key) WHERE achievement_key LIKE '%millionaire%' OR achievement_key LIKE '%collector%';
CREATE INDEX idx_achievements_mission ON achievements(achievement_key) WHERE achievement_key LIKE '%dedicated%' OR achievement_key LIKE '%mission%';