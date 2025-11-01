-- Migration 012: Create Configuration Manager tables
-- This migration adds tables for unified configuration management

-- Config templates table
CREATE TABLE config_templates (
    id SERIAL PRIMARY KEY,
    template_key VARCHAR(100) UNIQUE NOT NULL,
    template_type VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    template_schema JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Config instances table
CREATE TABLE config_instances (
    id SERIAL PRIMARY KEY,
    template_id INTEGER REFERENCES config_templates(id),
    instance_data JSONB NOT NULL,
    created_by INTEGER,
    status VARCHAR(50) DEFAULT 'draft',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Config versions table for tracking changes
CREATE TABLE config_versions (
    id SERIAL PRIMARY KEY,
    config_instance_id INTEGER REFERENCES config_instances(id),
    version_number INTEGER NOT NULL,
    changed_by INTEGER,
    changes JSONB NOT NULL,
    change_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    can_rollback BOOLEAN DEFAULT TRUE
);

-- Create indexes for performance
CREATE INDEX idx_config_templates_key ON config_templates(template_key);
CREATE INDEX idx_config_templates_type ON config_templates(template_type);
CREATE INDEX idx_config_templates_active ON config_templates(is_active);
CREATE INDEX idx_config_instances_template ON config_instances(template_id);
CREATE INDEX idx_config_instances_status ON config_instances(status);
CREATE INDEX idx_config_instances_created ON config_instances(created_at);
CREATE INDEX idx_config_versions_instance ON config_versions(config_instance_id);
CREATE INDEX idx_config_versions_number ON config_versions(version_number);

-- Insert basic configuration templates
INSERT INTO config_templates (template_key, template_type, name, description, template_schema) VALUES
(
    'narrative_experience',
    'experience',
    'Narrative Experience Template',
    'Template for creating narrative experiences with gamification elements',
    '{
        "type": "object",
        "required": ["name", "description", "fragments"],
        "properties": {
            "name": {"type": "string", "minLength": 3, "maxLength": 100},
            "description": {"type": "string", "minLength": 10, "maxLength": 500},
            "fragments": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "required": ["title", "content", "decisions"],
                    "properties": {
                        "title": {"type": "string", "minLength": 3, "maxLength": 100},
                        "content": {"type": "string", "minLength": 10},
                        "decisions": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "required": ["text", "next_fragment"],
                                "properties": {
                                    "text": {"type": "string", "minLength": 3, "maxLength": 100},
                                    "next_fragment": {"type": "string", "minLength": 1}
                                }
                            }
                        }
                    }
                }
            },
            "rewards": {
                "type": "object",
                "properties": {
                    "besitos": {"type": "integer", "minimum": 0, "maximum": 1000},
                    "items": {"type": "array", "items": {"type": "string"}},
                    "achievements": {"type": "array", "items": {"type": "string"}}
                }
            },
            "requirements": {
                "type": "object",
                "properties": {
                    "besitos": {"type": "integer", "minimum": 0},
                    "items": {"type": "array", "items": {"type": "string"}},
                    "is_vip": {"type": "boolean"}
                }
            }
        }
    }'
),
(
    'mission_template',
    'mission',
    'Mission Template',
    'Template for creating missions with requirements and rewards',
    '{
        "type": "object",
        "required": ["title", "description", "mission_type", "requirements", "rewards"],
        "properties": {
            "title": {"type": "string", "minLength": 3, "maxLength": 100},
            "description": {"type": "string", "minLength": 10, "maxLength": 500},
            "mission_type": {"type": "string", "enum": ["daily", "weekly", "narrative", "special"]},
            "recurrence": {"type": "string", "enum": ["once", "daily", "weekly"]},
            "requirements": {
                "type": "object",
                "properties": {
                    "complete_fragments": {"type": "array", "items": {"type": "string"}},
                    "collect_items": {"type": "array", "items": {"type": "string"}},
                    "earn_besitos": {"type": "integer", "minimum": 0},
                    "unlock_achievements": {"type": "array", "items": {"type": "string"}}
                }
            },
            "rewards": {
                "type": "object",
                "properties": {
                    "besitos": {"type": "integer", "minimum": 0, "maximum": 500},
                    "items": {"type": "array", "items": {"type": "string"}},
                    "achievements": {"type": "array", "items": {"type": "string"}}
                }
            },
            "expiry_date": {"type": "string", "format": "date-time"}
        }
    }'
),
(
    'event_template',
    'event',
    'Event Template',
    'Template for creating special events with time-limited content',
    '{
        "type": "object",
        "required": ["name", "description", "start_date", "end_date"],
        "properties": {
            "name": {"type": "string", "minLength": 3, "maxLength": 100},
            "description": {"type": "string", "minLength": 10, "maxLength": 500},
            "start_date": {"type": "string", "format": "date-time"},
            "end_date": {"type": "string", "format": "date-time"},
            "event_type": {"type": "string", "enum": ["seasonal", "special", "anniversary"]},
            "content": {
                "type": "object",
                "properties": {
                    "narrative_experiences": {"type": "array", "items": {"type": "string"}},
                    "special_missions": {"type": "array", "items": {"type": "string"}},
                    "exclusive_items": {"type": "array", "items": {"type": "string"}}
                }
            },
            "rewards": {
                "type": "object",
                "properties": {
                    "participation": {"type": "integer", "minimum": 0},
                    "completion": {"type": "integer", "minimum": 0},
                    "special_items": {"type": "array", "items": {"type": "string"}}
                }
            }
        }
    }'
);