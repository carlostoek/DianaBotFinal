-- Create experiences tables for unified experiences system

-- Experiences table
CREATE TABLE experiences (
    id SERIAL PRIMARY KEY,
    experience_key VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    experience_type VARCHAR(50) NOT NULL,
    
    -- Configuración
    is_active BOOLEAN DEFAULT TRUE,
    is_visible BOOLEAN DEFAULT TRUE,
    difficulty_level VARCHAR(50) DEFAULT 'normal',
    estimated_duration INTEGER,
    
    -- Métricas
    start_count INTEGER DEFAULT 0,
    completion_count INTEGER DEFAULT 0,
    average_completion_time FLOAT DEFAULT 0.0,
    success_rate FLOAT DEFAULT 0.0,
    
    -- Metadata
    tags TEXT[],
    experience_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Experience components table
CREATE TABLE experience_components (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER NOT NULL REFERENCES experiences(id) ON DELETE CASCADE,
    component_key VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Configuración
    component_type VARCHAR(50) NOT NULL,
    sequence_order INTEGER NOT NULL,
    is_optional BOOLEAN DEFAULT FALSE,
    
    -- Requisitos y recompensas específicas
    component_requirements JSONB,
    completion_rewards JSONB,
    
    -- Metadata
    component_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User experience progress table
CREATE TABLE user_experience_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    experience_id INTEGER NOT NULL REFERENCES experiences(id) ON DELETE CASCADE,
    
    -- Estado del progreso
    status VARCHAR(50) NOT NULL,
    current_component_id INTEGER REFERENCES experience_components(id),
    
    -- Métricas de progreso
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    last_activity_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Progreso numérico
    completion_percentage FLOAT DEFAULT 0.0,
    components_completed INTEGER DEFAULT 0,
    components_total INTEGER DEFAULT 0,
    
    -- Metadata
    progress_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- User component completions table
CREATE TABLE user_component_completions (
    id SERIAL PRIMARY KEY,
    user_progress_id INTEGER NOT NULL REFERENCES user_experience_progress(id) ON DELETE CASCADE,
    component_id INTEGER NOT NULL REFERENCES experience_components(id) ON DELETE CASCADE,
    
    -- Datos de completitud
    completed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completion_data JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Experience requirements table
CREATE TABLE experience_requirements (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER NOT NULL REFERENCES experiences(id) ON DELETE CASCADE,
    
    -- Tipo de requisito
    requirement_type VARCHAR(50) NOT NULL,
    requirement_value JSONB NOT NULL,
    
    -- Configuración
    is_mandatory BOOLEAN DEFAULT TRUE,
    requirement_order INTEGER DEFAULT 0,
    
    -- Metadata
    requirement_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Experience rewards table
CREATE TABLE experience_rewards (
    id SERIAL PRIMARY KEY,
    experience_id INTEGER NOT NULL REFERENCES experiences(id) ON DELETE CASCADE,
    
    -- Tipo de recompensa
    reward_type VARCHAR(50) NOT NULL,
    reward_value JSONB NOT NULL,
    
    -- Configuración
    reward_order INTEGER DEFAULT 0,
    is_guaranteed BOOLEAN DEFAULT TRUE,
    
    -- Metadata
    reward_metadata JSONB,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_experiences_key ON experiences(experience_key);
CREATE INDEX idx_experiences_type ON experiences(experience_type);
CREATE INDEX idx_experiences_active ON experiences(is_active);

CREATE INDEX idx_experience_components_experience_id ON experience_components(experience_id);
CREATE INDEX idx_experience_components_key ON experience_components(component_key);
CREATE INDEX idx_experience_components_type ON experience_components(component_type);
CREATE INDEX idx_experience_components_order ON experience_components(experience_id, sequence_order);

CREATE INDEX idx_user_experience_progress_user_id ON user_experience_progress(user_id);
CREATE INDEX idx_user_experience_progress_experience_id ON user_experience_progress(experience_id);
CREATE INDEX idx_user_experience_progress_status ON user_experience_progress(status);
CREATE INDEX idx_user_experience_progress_user_experience ON user_experience_progress(user_id, experience_id);

CREATE INDEX idx_user_component_completions_user_progress_id ON user_component_completions(user_progress_id);
CREATE INDEX idx_user_component_completions_component_id ON user_component_completions(component_id);
CREATE INDEX idx_user_component_completions_user_component ON user_component_completions(user_progress_id, component_id);

CREATE INDEX idx_experience_requirements_experience_id ON experience_requirements(experience_id);
CREATE INDEX idx_experience_requirements_type ON experience_requirements(requirement_type);

CREATE INDEX idx_experience_rewards_experience_id ON experience_rewards(experience_id);
CREATE INDEX idx_experience_rewards_type ON experience_rewards(reward_type);

-- Add unique constraints
ALTER TABLE user_experience_progress ADD CONSTRAINT unique_user_experience UNIQUE (user_id, experience_id);
ALTER TABLE user_component_completions ADD CONSTRAINT unique_user_component_completion UNIQUE (user_progress_id, component_id);

-- Insert sample experiences for testing
INSERT INTO experiences (experience_key, name, description, experience_type, difficulty_level, estimated_duration, tags) VALUES
('first_quest', 'La Primera Aventura', 'Una experiencia introductoria para nuevos usuarios', 'narrative_chain', 'easy', 30, ARRAY['intro', 'tutorial', 'beginner']),
('mystery_solver', 'Resolvedor de Misterios', 'Desentraña secretos y resuelve acertijos', 'mixed', 'normal', 60, ARRAY['mystery', 'puzzle', 'interactive']),
('vip_journey', 'Viaje VIP', 'Experiencia exclusiva para miembros VIP', 'mission_chain', 'hard', 120, ARRAY['vip', 'exclusive', 'premium']);

-- Insert sample components for first_quest
INSERT INTO experience_components (experience_id, component_key, name, description, component_type, sequence_order, component_requirements, completion_rewards) VALUES
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'welcome_message', 'Mensaje de Bienvenida', 'Recibe la bienvenida al mundo de Diana', 'narrative', 1, '{"type": "none"}', '{"besitos": 10}'),
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'first_mission', 'Primera Misión', 'Completa tu primera misión', 'mission', 2, '{"type": "level", "min_level": 1}', '{"besitos": 25, "item": "basic_sword"}'),
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'intro_trivia', 'Trivia Introductoria', 'Demuestra tu conocimiento básico', 'trivia', 3, '{"type": "trivia_completion"}', '{"besitos": 15}');

-- Insert sample requirements for first_quest
INSERT INTO experience_requirements (experience_id, requirement_type, requirement_value, is_mandatory, requirement_order) VALUES
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'level', '{"min_level": 1}', TRUE, 1),
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'vip_membership', '{"required": false}', FALSE, 2);

-- Insert sample rewards for first_quest
INSERT INTO experience_rewards (experience_id, reward_type, reward_value, reward_order, is_guaranteed) VALUES
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'besitos', '{"amount": 100}', 1, TRUE),
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'achievement', '{"achievement_key": "first_experience_completed"}', 2, TRUE),
((SELECT id FROM experiences WHERE experience_key = 'first_quest'), 'narrative_unlock', '{"fragment_key": "quest_completion_reveal"}', 3, TRUE);