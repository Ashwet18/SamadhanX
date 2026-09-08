-- SamadhanX PostgreSQL Initialization Script
-- This script sets up required extensions and initial configurations

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "btree_gist";

-- Set timezone
SET timezone = 'Asia/Kolkata';

-- Create custom functions for common operations
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create function for soft delete
CREATE OR REPLACE FUNCTION soft_delete_record()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE SET 
        is_deleted = true,
        deleted_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
    RETURN NULL;
END;
$$ language 'plpgsql';

-- Create function for search vector updates
CREATE OR REPLACE FUNCTION update_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector = 
        setweight(to_tsvector('english', coalesce(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(NEW.location_description, '')), 'C');
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Grant usage on extensions
GRANT USAGE ON SCHEMA public TO samadhanx;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO samadhanx;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO samadhanx;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO samadhanx;