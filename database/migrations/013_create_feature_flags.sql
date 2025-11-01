-- Migration 013: Create Feature Flags System
-- This migration adds the feature flag template for gradual rollout management

-- Insert feature flag configuration template
INSERT INTO config_templates (template_key, template_type, name, description, template_schema) VALUES
(
    'feature_flag',
    'feature',
    'Feature Flag Template',
    'Template for managing feature flags with gradual rollout and beta testing',
    '{
        "type": "object",
        "required": ["name", "enabled"],
        "properties": {
            "name": {
                "type": "string",
                "minLength": 3,
                "maxLength": 100
            },
            "description": {
                "type": "string",
                "maxLength": 500
            },
            "enabled": {
                "type": "boolean"
            },
            "rollout_percentage": {
                "type": "integer",
                "minimum": 0,
                "maximum": 100
            },
            "beta_testers": {
                "type": "array",
                "items": {
                    "type": "integer"
                }
            },
            "created_at": {
                "type": "string",
                "format": "date-time"
            }
        }
    }'
);

-- Create initial feature flags for the system
INSERT INTO config_instances (template_id, instance_data, status) VALUES
(
    (SELECT id FROM config_templates WHERE template_key = 'feature_flag'),
    '{
        "name": "experiences",
        "description": "Narrative experiences system",
        "enabled": false,
        "rollout_percentage": 0,
        "beta_testers": [],
        "created_at": "2025-01-01T00:00:00Z"
    }',
    'active'
),
(
    (SELECT id FROM config_templates WHERE template_key = 'feature_flag'),
    '{
        "name": "auctions",
        "description": "Auction system for rare items",
        "enabled": false,
        "rollout_percentage": 0,
        "beta_testers": [],
        "created_at": "2025-01-01T00:00:00Z"
    }',
    'active'
),
(
    (SELECT id FROM config_templates WHERE template_key = 'feature_flag'),
    '{
        "name": "achievements",
        "description": "Achievement system with rewards",
        "enabled": false,
        "rollout_percentage": 0,
        "beta_testers": [],
        "created_at": "2025-01-01T00:00:00Z"
    }',
    'active'
);