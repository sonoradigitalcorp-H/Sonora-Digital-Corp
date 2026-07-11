-- Content System for Avatar Pipeline
-- Depends on: artists table (009_content_system.sql)
-- Part of: Sprint 0 — Contenido AI ($29.99/mes) + White Label ($299/mes)

CREATE TABLE IF NOT EXISTS voice_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    name TEXT NOT NULL DEFAULT 'default',
    provider TEXT NOT NULL DEFAULT 'omnivoice',
    voice_id TEXT NOT NULL,
    language TEXT NOT NULL DEFAULT 'es',
    is_cloned BOOLEAN NOT NULL DEFAULT FALSE,
    sample_audio_url TEXT,
    settings JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_voice_profiles_artist ON voice_profiles(artist_id);

CREATE TABLE IF NOT EXISTS lora_models (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','training','ready','failed')),
    file_url TEXT,
    trigger_word TEXT,
    source_photos INT NOT NULL DEFAULT 0,
    training_cost_usd NUMERIC(6,4) NOT NULL DEFAULT 0,
    trained_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_lora_models_artist ON lora_models(artist_id);

CREATE TABLE IF NOT EXISTS templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'social'
        CHECK (category IN ('social','story','music_video','talking_head','promo','nsfw')),
    engine TEXT NOT NULL DEFAULT 'agnes'
        CHECK (engine IN ('agnes','muapi','fal','omnivoice','openai')),
    prompt_template TEXT NOT NULL,
    negative_prompt TEXT NOT NULL DEFAULT '',
    width INT NOT NULL DEFAULT 1024,
    height INT NOT NULL DEFAULT 1024,
    steps INT NOT NULL DEFAULT 30,
    cfg_scale NUMERIC(3,1) NOT NULL DEFAULT 7.0,
    use_lora BOOLEAN NOT NULL DEFAULT FALSE,
    use_voice BOOLEAN NOT NULL DEFAULT FALSE,
    is_nsfw BOOLEAN NOT NULL DEFAULT FALSE,
    cost_estimate_usd NUMERIC(6,4) NOT NULL DEFAULT 0,
    virality_score NUMERIC(4,3) NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    template_id UUID REFERENCES templates(id),
    lora_model_id UUID REFERENCES lora_models(id),
    voice_profile_id UUID REFERENCES voice_profiles(id),
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK (status IN ('queued','processing','completed','failed','cancelled')),
    media_type TEXT NOT NULL
        CHECK (media_type IN ('image','video','audio','talking_head')),
    prompt TEXT NOT NULL,
    output_urls JSONB NOT NULL DEFAULT '[]',
    nsfw BOOLEAN NOT NULL DEFAULT FALSE,
    cost_usd NUMERIC(8,6),
    duration_ms INT,
    error TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    completed_at TIMESTAMPTZ
);
CREATE INDEX idx_generations_artist ON generations(artist_id);
CREATE INDEX idx_generations_status ON generations(status);
CREATE INDEX idx_generations_created ON generations(created_at DESC);

CREATE TABLE IF NOT EXISTS content_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    generation_id UUID REFERENCES generations(id) ON DELETE SET NULL,
    priority INT NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','running','completed','failed')),
    scheduled_for TIMESTAMPTZ,
    platform TEXT NOT NULL DEFAULT 'telegram'
        CHECK (platform IN ('telegram','whatsapp','instagram','tiktok','youtube')),
    engaged INT NOT NULL DEFAULT 0,
    views INT NOT NULL DEFAULT 0,
    engagement_rate NUMERIC(5,4) NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);
CREATE INDEX idx_content_queue_artist ON content_queue(artist_id);
CREATE INDEX idx_content_queue_scheduled ON content_queue(scheduled_for) WHERE status = 'pending';

CREATE TABLE IF NOT EXISTS product_tiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    price_usd NUMERIC(8,2) NOT NULL,
    setup_fee_usd NUMERIC(8,2) NOT NULL DEFAULT 0,
    max_generations INT NOT NULL DEFAULT 30,
    max_video_seconds INT NOT NULL DEFAULT 60,
    has_lora BOOLEAN NOT NULL DEFAULT FALSE,
    has_voice_clone BOOLEAN NOT NULL DEFAULT FALSE,
    has_talking_head BOOLEAN NOT NULL DEFAULT FALSE,
    has_nsfw BOOLEAN NOT NULL DEFAULT FALSE,
    has_ai_calls BOOLEAN NOT NULL DEFAULT FALSE,
    white_label BOOLEAN NOT NULL DEFAULT FALSE,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

INSERT INTO product_tiers (name, price_usd, setup_fee_usd, max_generations, max_video_seconds, has_lora, has_voice_clone, has_talking_head, has_nsfw, has_ai_calls, white_label, metadata) VALUES
    ('Contenido AI', 29.99, 0, 30, 60, FALSE, TRUE, TRUE, FALSE, FALSE, FALSE, '{"description": "Entry-level AI content for musicians", "features": ["reference_images", "voice_clone", "talking_head", "notebooklm_story"]}'),
    ('White Label', 299.00, 49, 9999, 600, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, '{"description": "Full white-label with dedicated LoRA", "features": ["lora_training", "voice_clone", "talking_head", "ai_calls", "nsfw", "unlimited"]}'),
    ('AI Calls', 49.00, 0, 0, 0, FALSE, TRUE, FALSE, FALSE, TRUE, FALSE, '{"description": "Add-on: AI calls to fans with artist voice", "features": ["voice_clone", "outbound_calls", "fan_outreach"]}'),
    ('LoRA Training', 49.00, 0, 0, 0, TRUE, FALSE, FALSE, FALSE, FALSE, FALSE, '{"description": "One-time LoRA training service", "features": ["dedicated_lora", "flux_model", "face_consistency"]}');
