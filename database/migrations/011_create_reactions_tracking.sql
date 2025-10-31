-- Migration 011: Create user_reactions table for gamified reactions tracking

CREATE TABLE IF NOT EXISTS user_reactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    post_id INTEGER NOT NULL,
    emoji VARCHAR(50) NOT NULL,
    rewarded_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_user_reactions_user_id ON user_reactions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_reactions_post_id ON user_reactions(post_id);
CREATE INDEX IF NOT EXISTS idx_user_reactions_emoji ON user_reactions(emoji);
CREATE INDEX IF NOT EXISTS idx_user_reactions_user_post_emoji ON user_reactions(user_id, post_id, emoji);

-- Add reaction_rewards column to channel_posts
ALTER TABLE channel_posts ADD COLUMN IF NOT EXISTS reaction_rewards JSONB;