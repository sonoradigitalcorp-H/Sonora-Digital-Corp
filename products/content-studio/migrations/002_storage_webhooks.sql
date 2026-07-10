-- Content Storage + Webhooks
ALTER TABLE generations ADD COLUMN IF NOT EXISTS local_url TEXT;
ALTER TABLE generations ADD COLUMN IF NOT EXISTS file_size_bytes BIGINT;
ALTER TABLE generations ADD COLUMN IF NOT EXISTS file_type TEXT;

CREATE TABLE IF NOT EXISTS content_webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    artist_id TEXT NOT NULL,
    url TEXT NOT NULL,
    secret TEXT,
    events TEXT[] NOT NULL DEFAULT '{"generation.completed"}',
    active BOOLEAN NOT NULL DEFAULT TRUE,
    last_delivery_at TIMESTAMPTZ,
    failure_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_content_webhooks_artist ON content_webhooks(artist_id);

CREATE TABLE IF NOT EXISTS content_deliveries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    webhook_id UUID REFERENCES content_webhooks(id) ON DELETE CASCADE,
    generation_id UUID REFERENCES generations(id) ON DELETE SET NULL,
    event TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','delivered','failed','retrying')),
    payload JSONB,
    response_code INT,
    response_body TEXT,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_content_deliveries_webhook ON content_deliveries(webhook_id);
