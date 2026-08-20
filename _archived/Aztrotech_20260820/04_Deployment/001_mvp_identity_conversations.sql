-- Migration: Cross-Canal Identity + Conversations + Messages + Metrics
-- MVP RAG-First + Memoria Persistente

BEGIN;

-- ── 1. Identity ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_identities (
    internal_id UUID PRIMARY KEY,
    platform VARCHAR(20) NOT NULL,
    platform_id VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    phone_e164 VARCHAR(20),
    email VARCHAR(200),
    locale VARCHAR(10) DEFAULT 'es',
    lead_type VARCHAR(10),
    lead_confidence FLOAT DEFAULT 0.0,
    business_name VARCHAR(200),
    business_type VARCHAR(100),
    pain_points JSONB DEFAULT '[]',
    budget_range VARCHAR(50),
    timeline VARCHAR(50),
    preferred_contact VARCHAR(20),
    conversation_count INT DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    merged_into UUID REFERENCES user_identities(internal_id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_interaction TIMESTAMPTZ,
    UNIQUE(platform, platform_id)
);

CREATE INDEX IF NOT EXISTS idx_identities_phone ON user_identities(phone_e164);
CREATE INDEX IF NOT EXISTS idx_identities_email ON user_identities(email);
CREATE INDEX IF NOT EXISTS idx_identities_lead ON user_identities(lead_type);

-- ── 2. Conversations ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY,
    internal_user_id UUID REFERENCES user_identities(internal_id),
    platform VARCHAR(20) NOT NULL,
    platform_conversation_id VARCHAR(100),
    lead_type VARCHAR(10),
    lead_confidence FLOAT,
    emotion_snapshot JSONB DEFAULT '{}',
    language VARCHAR(10) DEFAULT 'es',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    closed_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_convs_user ON conversations(internal_user_id);
CREATE INDEX IF NOT EXISTS idx_convs_lead ON conversations(lead_type);

-- ── 3. Messages (token tracking + RAG/emotion audit) ──────────
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    turn_number INT NOT NULL,
    role VARCHAR(10) NOT NULL,
    content TEXT NOT NULL,
    tokens_in INT,
    tokens_out INT,
    model VARCHAR(80),
    cost_usd DECIMAL(12,6),
    emotion_scores JSONB DEFAULT '{}',
    rag_chunks_used JSONB DEFAULT '[]',
    emerge_layers_used JSONB DEFAULT '{}',
    language VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_messages_conv ON messages(conversation_id, turn_number);
CREATE INDEX IF NOT EXISTS idx_messages_model ON messages(model);
CREATE INDEX IF NOT EXISTS idx_messages_created ON messages(created_at);

-- ── 4. Metrics / Daily aggregates ──────────────────────────────
CREATE TABLE IF NOT EXISTS daily_metrics (
    day DATE PRIMARY KEY,
    total_conversations INT DEFAULT 0,
    total_messages INT DEFAULT 0,
    leads_cold INT DEFAULT 0,
    leads_warm INT DEFAULT 0,
    leads_hot INT DEFAULT 0,
    tokens_in BIGINT DEFAULT 0,
    tokens_out BIGINT DEFAULT 0,
    cost_usd DECIMAL(14,6) DEFAULT 0,
    avg_latency_ms INT DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ── 5. Emerge memory promotions (audit trail) ──────────────────
CREATE TABLE IF NOT EXISTS emerge_promotions (
    id SERIAL PRIMARY KEY,
    internal_user_id UUID REFERENCES user_identities(internal_id),
    from_layer INT NOT NULL,
    to_layer INT NOT NULL,
    key TEXT NOT NULL,
    criteria TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_emerge_promos ON emerge_promotions(internal_user_id, to_layer);

COMMIT;
