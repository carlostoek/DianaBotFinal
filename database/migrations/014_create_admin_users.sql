-- Migration 014: Create admin users table for API authentication

CREATE TABLE admin_users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'admin',
    is_active BOOLEAN DEFAULT TRUE,
    permissions JSONB,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX idx_admin_users_username ON admin_users(username);
CREATE INDEX idx_admin_users_email ON admin_users(email);
CREATE INDEX idx_admin_users_role ON admin_users(role);
CREATE INDEX idx_admin_users_is_active ON admin_users(is_active);

-- Insert default admin user (password will be set via application)
INSERT INTO admin_users (username, email, hashed_password, role) 
VALUES ('admin', 'admin@dianabot.com', '$2b$12$placeholder_for_hashed_password', 'owner');

COMMENT ON TABLE admin_users IS 'Admin users for API authentication and management';
COMMENT ON COLUMN admin_users.username IS 'Unique username for admin login';
COMMENT ON COLUMN admin_users.email IS 'Admin email address';
COMMENT ON COLUMN admin_users.hashed_password IS 'BCrypt hashed password';
COMMENT ON COLUMN admin_users.role IS 'Admin role: owner, admin, moderator, content_creator';
COMMENT ON COLUMN admin_users.is_active IS 'Whether the admin account is active';
COMMENT ON COLUMN admin_users.permissions IS 'Additional permissions beyond role';
COMMENT ON COLUMN admin_users.last_login IS 'Last login timestamp';
COMMENT ON COLUMN admin_users.created_at IS 'Account creation timestamp';
COMMENT ON COLUMN admin_users.updated_at IS 'Last update timestamp';