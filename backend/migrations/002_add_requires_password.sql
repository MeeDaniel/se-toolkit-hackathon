-- Migration: Add requires_password column to users table
-- Date: 2026-04-06
-- Purpose: Distinguish between users who MUST have passwords (Telegram) and those who don't (web-only)

-- Add requires_password column (default 0 = false for existing users)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'requires_password'
    ) THEN
        ALTER TABLE users ADD COLUMN requires_password INTEGER DEFAULT 0 NOT NULL;
    END IF;
END $$;
