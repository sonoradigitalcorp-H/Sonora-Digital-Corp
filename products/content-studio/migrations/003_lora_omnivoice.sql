-- Migration 003: LoRA weights + OmniVoice profile_id column
-- Date: 2026-07-10

CREATE TABLE IF NOT EXISTS lora_weights (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL DEFAULT 'default',
    path TEXT NOT NULL,
    scale DOUBLE PRECISION NOT NULL DEFAULT 0.8,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lora_weights_artist ON lora_weights(artist_id);

-- Add omnivoice_profile_id to voice_profiles for tracking
ALTER TABLE voice_profiles ADD COLUMN IF NOT EXISTS omnivoice_profile_id VARCHAR(255);
ALTER TABLE voice_profiles ADD COLUMN IF NOT EXISTS status VARCHAR(50) NOT NULL DEFAULT 'pending';
