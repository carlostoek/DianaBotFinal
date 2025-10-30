-- Create user_balances and transactions tables for besitos economy
CREATE TABLE IF NOT EXISTS user_balances (
    user_id INTEGER PRIMARY KEY,
    besitos INTEGER DEFAULT 0 NOT NULL,
    lifetime_besitos INTEGER DEFAULT 0 NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    amount INTEGER NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    source VARCHAR(100) NOT NULL,
    description TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for transactions table
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_created_at ON transactions(created_at);
CREATE INDEX IF NOT EXISTS idx_transactions_source ON transactions(source);

-- Add foreign key constraint for user_balances
ALTER TABLE user_balances 
ADD CONSTRAINT fk_user_balances_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Add foreign key constraint for transactions
ALTER TABLE transactions 
ADD CONSTRAINT fk_transactions_user_id 
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;