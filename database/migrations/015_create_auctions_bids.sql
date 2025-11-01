-- Migration 015: Create auctions and bids tables

-- Auctions table
CREATE TABLE IF NOT EXISTS auctions (
    auction_id SERIAL PRIMARY KEY,
    item_id INTEGER REFERENCES items(id) NOT NULL,
    auction_type VARCHAR(50) NOT NULL DEFAULT 'standard', -- 'standard', 'dutch', 'silent'
    start_price INTEGER NOT NULL CHECK (start_price >= 0),
    current_bid INTEGER NOT NULL CHECK (current_bid >= 0),
    current_bidder_id BIGINT REFERENCES users(id),
    winner_id BIGINT REFERENCES users(id),
    status VARCHAR(50) NOT NULL DEFAULT 'active', -- 'active', 'closed', 'cancelled'
    start_time TIMESTAMP NOT NULL DEFAULT NOW(),
    end_time TIMESTAMP NOT NULL,
    extended_end_time TIMESTAMP, -- For dynamic timer extension
    min_bid_increment INTEGER NOT NULL DEFAULT 10,
    bid_count INTEGER NOT NULL DEFAULT 0,
    auction_metadata JSONB, -- Additional auction settings
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Bids table
CREATE TABLE IF NOT EXISTS bids (
    bid_id SERIAL PRIMARY KEY,
    auction_id INTEGER REFERENCES auctions(auction_id) NOT NULL,
    user_id BIGINT REFERENCES users(id) NOT NULL,
    amount INTEGER NOT NULL CHECK (amount > 0),
    is_winning BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(auction_id, user_id, amount) -- Prevent duplicate bids
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_auctions_status_end_time ON auctions(status, end_time);
CREATE INDEX IF NOT EXISTS idx_auctions_item_id ON auctions(item_id);
CREATE INDEX IF NOT EXISTS idx_bids_auction_id ON bids(auction_id);
CREATE INDEX IF NOT EXISTS idx_bids_user_id ON bids(user_id);
CREATE INDEX IF NOT EXISTS idx_bids_created_at ON bids(created_at);

-- Add auction-related events to event_logs
INSERT INTO event_types (event_type, description) VALUES 
    ('auction_started', 'Auction started'),
    ('bid_placed', 'Bid placed in auction'),
    ('auction_won', 'Auction won by user'),
    ('auction_closed', 'Auction closed without winner')
ON CONFLICT (event_type) DO NOTHING;