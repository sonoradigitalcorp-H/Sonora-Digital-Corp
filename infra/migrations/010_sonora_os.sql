-- Sonora OS Foundation Schema
-- Part of: SPEC-20260712-SONORA-001
-- Depends on: PostgreSQL 15+
-- Migrates from: JSON file-based storage to relational multi-tenant DB
-- Hasura: all tables tracked in public schema with RLS

-- ─── Extensions ───

CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─── ENUMS ───

CREATE TYPE tenant_plan AS ENUM ('lanzamiento', 'crecimiento', 'ilimitado', 'enterprise');
CREATE TYPE user_role AS ENUM ('platform_admin', 'client_admin', 'artist', 'fan');
CREATE TYPE greeting_status AS ENUM ('pending_payment', 'paid', 'generating', 'pending_approval', 'approved', 'rejected', 'delivered', 'refunded');
CREATE TYPE transaction_status AS ENUM ('pending', 'completed', 'failed', 'refunded');
CREATE TYPE transaction_type AS ENUM ('earn_beat', 'burn_beat', 'transfer_beat', 'stripe_payment', 'stripe_payout', 'reward', 'referral');
CREATE TYPE quest_category AS ENUM ('play', 'work', 'learn');
CREATE TYPE quest_frequency AS ENUM ('daily', 'weekly', 'monthly', 'one_time');
CREATE TYPE message_channel AS ENUM ('telegram', 'whatsapp', 'web', 'voice');
CREATE TYPE content_type AS ENUM ('image', 'video', 'audio', 'talking_head');
CREATE TYPE content_status AS ENUM ('queued', 'generating', 'completed', 'failed');

-- ─── TABLE: tenants ───

CREATE TABLE IF NOT EXISTS tenants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    plan tenant_plan NOT NULL DEFAULT 'lanzamiento',
    is_active BOOLEAN NOT NULL DEFAULT true,
    beat_supply BIGINT NOT NULL DEFAULT 0,
    config JSONB NOT NULL DEFAULT '{}',
    branding JSONB NOT NULL DEFAULT '{"primary_color":"#6366f1","logo_url":null}',
    pricing_config JSONB NOT NULL DEFAULT '{"beat_per_usd":10,"greeting_beat_cost":50,"greeting_usd_cost":5}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_tenants_slug ON tenants(slug);
CREATE INDEX idx_tenants_active ON tenants(is_active);

-- ─── TABLE: users ───

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    email TEXT,
    phone TEXT,
    display_name TEXT NOT NULL,
    role user_role NOT NULL DEFAULT 'fan',
    avatar_url TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT users_email_or_phone CHECK (email IS NOT NULL OR phone IS NOT NULL)
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- ─── TABLE: telegram_users ───

CREATE TABLE IF NOT EXISTS telegram_users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    telegram_id BIGINT UNIQUE NOT NULL,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    telegram_username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT DEFAULT 'es',
    is_bot_blocked BOOLEAN NOT NULL DEFAULT false,
    last_interaction_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_telegram_users_tid ON telegram_users(telegram_id);
CREATE INDEX idx_telegram_users_tenant ON telegram_users(tenant_id);
CREATE INDEX idx_telegram_users_user ON telegram_users(user_id);

-- ─── TABLE: token_ledger ───

CREATE TABLE IF NOT EXISTS token_ledger (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    transaction_type transaction_type NOT NULL,
    amount BIGINT NOT NULL,
    balance_after BIGINT NOT NULL,
    reference_type TEXT,
    reference_id TEXT,
    description TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_token_ledger_tenant ON token_ledger(tenant_id);
CREATE INDEX idx_token_ledger_user ON token_ledger(user_id);
CREATE INDEX idx_token_ledger_type ON token_ledger(transaction_type);
CREATE INDEX idx_token_ledger_created ON token_ledger(created_at DESC);

-- ─── TABLE: greetings ───

CREATE TABLE IF NOT EXISTS greetings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    artist_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    fan_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    status greeting_status NOT NULL DEFAULT 'pending_payment',
    beat_cost BIGINT NOT NULL DEFAULT 0,
    usd_cost NUMERIC(10,2) NOT NULL DEFAULT 0,
    audio_url TEXT,
    ai_generated BOOLEAN NOT NULL DEFAULT false,
    artist_approved_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_greetings_tenant ON greetings(tenant_id);
CREATE INDEX idx_greetings_artist ON greetings(artist_id);
CREATE INDEX idx_greetings_fan ON greetings(fan_id);
CREATE INDEX idx_greetings_status ON greetings(status);

-- ─── TABLE: transactions ───

CREATE TABLE IF NOT EXISTS transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(10,2) NOT NULL,
    currency TEXT NOT NULL DEFAULT 'usd',
    provider TEXT NOT NULL DEFAULT 'stripe',
    provider_transaction_id TEXT,
    status transaction_status NOT NULL DEFAULT 'pending',
    description TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_transactions_tenant ON transactions(tenant_id);
CREATE INDEX idx_transactions_user ON transactions(user_id);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_provider ON transactions(provider, provider_transaction_id);

-- ─── TABLE: quests ───

CREATE TABLE IF NOT EXISTS quests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category quest_category NOT NULL,
    frequency quest_frequency NOT NULL DEFAULT 'daily',
    beat_reward BIGINT NOT NULL DEFAULT 0,
    xp_reward INT NOT NULL DEFAULT 0,
    requirements JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    starts_at TIMESTAMPTZ,
    ends_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_quests_tenant ON quests(tenant_id);
CREATE INDEX idx_quests_category ON quests(category);
CREATE INDEX idx_quests_active ON quests(is_active);

-- ─── TABLE: quest_completions ───

CREATE TABLE IF NOT EXISTS quest_completions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    quest_id UUID NOT NULL REFERENCES quests(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    completed_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_quest_completions_quest ON quest_completions(quest_id);
CREATE INDEX idx_quest_completions_user ON quest_completions(user_id);
CREATE INDEX idx_quest_completions_tenant ON quest_completions(tenant_id);
CREATE UNIQUE INDEX idx_quest_completions_unique ON quest_completions(quest_id, user_id);

-- ─── TABLE: rewards ───

CREATE TABLE IF NOT EXISTS rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    quest_completion_id UUID REFERENCES quest_completions(id) ON DELETE SET NULL,
    beat_amount BIGINT NOT NULL DEFAULT 0,
    xp_amount INT NOT NULL DEFAULT 0,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_rewards_tenant ON rewards(tenant_id);
CREATE INDEX idx_rewards_user ON rewards(user_id);

-- ─── TABLE: schedules ───

CREATE TABLE IF NOT EXISTS schedules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    cron_expression TEXT NOT NULL,
    timezone TEXT NOT NULL DEFAULT 'America/Mexico_City',
    days_of_week INT[] DEFAULT '{1,2,3,4,5,6,7}',
    start_time TIME NOT NULL DEFAULT '09:00',
    end_time TIME NOT NULL DEFAULT '18:00',
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_schedules_tenant ON schedules(tenant_id);
CREATE INDEX idx_schedules_active ON schedules(is_active);

-- ─── TABLE: auto_messages ───

CREATE TABLE IF NOT EXISTS auto_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    schedule_id UUID REFERENCES schedules(id) ON DELETE SET NULL,
    trigger_event TEXT,
    template TEXT NOT NULL,
    channel message_channel NOT NULL DEFAULT 'telegram',
    filters JSONB NOT NULL DEFAULT '{}',
    is_active BOOLEAN NOT NULL DEFAULT true,
    last_sent_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_auto_messages_tenant ON auto_messages(tenant_id);
CREATE INDEX idx_auto_messages_schedule ON auto_messages(schedule_id);
CREATE INDEX idx_auto_messages_active ON auto_messages(is_active);

-- ─── TABLE: notifications ───

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    channel message_channel NOT NULL DEFAULT 'telegram',
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    is_read BOOLEAN NOT NULL DEFAULT false,
    is_sent BOOLEAN NOT NULL DEFAULT false,
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_notifications_tenant ON notifications(tenant_id);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_sent ON notifications(is_sent);
CREATE INDEX idx_notifications_read ON notifications(is_read);

-- ─── TABLE: content_generations ───

CREATE TABLE IF NOT EXISTS content_generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    content_type content_type NOT NULL,
    status content_status NOT NULL DEFAULT 'queued',
    prompt TEXT NOT NULL,
    negative_prompt TEXT DEFAULT '',
    provider TEXT NOT NULL DEFAULT 'fal',
    provider_job_id TEXT,
    output_urls JSONB NOT NULL DEFAULT '[]',
    cost_usd NUMERIC(10,6) NOT NULL DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}',
    error_message TEXT,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_content_gen_tenant ON content_generations(tenant_id);
CREATE INDEX idx_content_gen_user ON content_generations(user_id);
CREATE INDEX idx_content_gen_status ON content_generations(status);
CREATE INDEX idx_content_gen_type ON content_generations(content_type);

-- ─── TABLE: scraped_metrics ───

CREATE TABLE IF NOT EXISTS scraped_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    artist_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    source TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value NUMERIC(20,4) NOT NULL,
    metric_unit TEXT NOT NULL DEFAULT 'count',
    raw_data JSONB,
    scraped_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_scraped_metrics_tenant ON scraped_metrics(tenant_id);
CREATE INDEX idx_scraped_metrics_artist ON scraped_metrics(artist_id);
CREATE INDEX idx_scraped_metrics_source ON scraped_metrics(source);
CREATE INDEX idx_scraped_metrics_name ON scraped_metrics(metric_name);
CREATE INDEX idx_scraped_metrics_time ON scraped_metrics(scraped_at DESC);

-- ─── TABLE: knowledge_bases ───

CREATE TABLE IF NOT EXISTS knowledge_bases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    qdrant_collection TEXT NOT NULL,
    open_notebook_project_id TEXT,
    document_count INT NOT NULL DEFAULT 0,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_knowledge_bases_tenant ON knowledge_bases(tenant_id);
CREATE UNIQUE INDEX idx_knowledge_bases_collection ON knowledge_bases(qdrant_collection);

-- ─── TABLE: agent_events (para WebSocket streaming) ───

CREATE TABLE IF NOT EXISTS agent_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    agent_name TEXT,
    session_id TEXT,
    payload JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_agent_events_tenant ON agent_events(tenant_id);
CREATE INDEX idx_agent_events_type ON agent_events(event_type);
CREATE INDEX idx_agent_events_created ON agent_events(created_at DESC);

-- ─── FUNCTION: update_updated_at() ───

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ─── TRIGGERS for updated_at ───

CREATE TRIGGER trg_tenants_updated_at
    BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_greetings_updated_at
    BEFORE UPDATE ON greetings
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_transactions_updated_at
    BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_quests_updated_at
    BEFORE UPDATE ON quests
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_schedules_updated_at
    BEFORE UPDATE ON schedules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_auto_messages_updated_at
    BEFORE UPDATE ON auto_messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_content_generations_updated_at
    BEFORE UPDATE ON content_generations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_knowledge_bases_updated_at
    BEFORE UPDATE ON knowledge_bases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- ─── ROW LEVEL SECURITY (multi-tenant isolation) ───

-- Enable RLS on all tenant-scoped tables
ALTER TABLE tenants ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE telegram_users ENABLE ROW LEVEL SECURITY;
ALTER TABLE token_ledger ENABLE ROW LEVEL SECURITY;
ALTER TABLE greetings ENABLE ROW LEVEL SECURITY;
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE quests ENABLE ROW LEVEL SECURITY;
ALTER TABLE quest_completions ENABLE ROW LEVEL SECURITY;
ALTER TABLE rewards ENABLE ROW LEVEL SECURITY;
ALTER TABLE schedules ENABLE ROW LEVEL SECURITY;
ALTER TABLE auto_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE content_generations ENABLE ROW LEVEL SECURITY;
ALTER TABLE scraped_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE knowledge_bases ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_events ENABLE ROW LEVEL SECURITY;

-- Platform admin: can see all
CREATE POLICY tenant_admin_all ON tenants
    FOR ALL USING (current_setting('hasura.role', true) = 'platform_admin');

CREATE POLICY user_admin_all ON users
    FOR ALL USING (current_setting('hasura.role', true) = 'platform_admin');

-- Client admin: can only see their own tenant's data
CREATE POLICY tenant_client_select ON tenants
    FOR SELECT USING (
        id::text = current_setting('hasura.tenant_id', true)
        AND current_setting('hasura.role', true) = 'client_admin'
    );

CREATE POLICY user_client_select ON users
    FOR SELECT USING (
        tenant_id::text = current_setting('hasura.tenant_id', true)
        AND current_setting('hasura.role', true) IN ('client_admin', 'artist', 'fan')
    );

-- Generic tenant-scoped RLS for all data tables
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT unnest(ARRAY[
            'telegram_users', 'token_ledger', 'greetings', 'transactions',
            'quests', 'quest_completions', 'rewards', 'schedules',
            'auto_messages', 'notifications', 'content_generations',
            'scraped_metrics', 'knowledge_bases', 'agent_events'
        ])
    LOOP
        EXECUTE format(
            'CREATE POLICY %s_tenant_select ON %s FOR SELECT USING (
                tenant_id::text = current_setting(''hasura.tenant_id'', true)
                AND current_setting(''hasura.role'', true) IN (''platform_admin'', ''client_admin'', ''artist'')
            )', tbl, tbl
        );
        EXECUTE format(
            'CREATE POLICY %s_tenant_insert ON %s FOR INSERT WITH CHECK (
                tenant_id::text = current_setting(''hasura.tenant_id'', true)
                AND current_setting(''hasura.role'', true) IN (''platform_admin'', ''client_admin'')
            )', tbl, tbl
        );
        EXECUTE format(
            'CREATE POLICY %s_tenant_update ON %s FOR UPDATE USING (
                tenant_id::text = current_setting(''hasura.tenant_id'', true)
                AND current_setting(''hasura.role'', true) IN (''platform_admin'', ''client_admin'')
            )', tbl, tbl
        );
        EXECUTE format(
            'CREATE POLICY %s_tenant_delete ON %s FOR DELETE USING (
                tenant_id::text = current_setting(''hasura.tenant_id'', true)
                AND current_setting(''hasura.role'', true) = ''platform_admin''
            )', tbl, tbl
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Seed data: default tenant
INSERT INTO tenants (slug, name, plan, beat_supply)
VALUES ('abe-music', 'ABE Music OS', 'ilimitado', 1000000)
ON CONFLICT (slug) DO NOTHING;

-- ─── ABE Music Business Tables (migrated from JSON files) ───

CREATE TABLE IF NOT EXISTS artists (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    legacy_id TEXT,
    name TEXT NOT NULL,
    genre TEXT,
    country TEXT,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'inactive', 'signed', 'archived')),
    email TEXT,
    phone TEXT,
    social JSONB NOT NULL DEFAULT '{}',
    streams BIGINT NOT NULL DEFAULT 0,
    revenue NUMERIC(14,2) NOT NULL DEFAULT 0,
    monthly_listeners INT NOT NULL DEFAULT 0,
    followers INT NOT NULL DEFAULT 0,
    top_song TEXT,
    top_song_streams BIGINT NOT NULL DEFAULT 0,
    youtube_views BIGINT NOT NULL DEFAULT 0,
    releases_count INT NOT NULL DEFAULT 0,
    contracts_count INT NOT NULL DEFAULT 0,
    spotify_url TEXT,
    apple_music_url TEXT,
    label TEXT,
    distribution TEXT,
    notable TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_artists_tenant ON artists(tenant_id);
CREATE INDEX idx_artists_status ON artists(status);
CREATE INDEX idx_artists_legacy ON artists(legacy_id);
ALTER TABLE artists ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS releases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    type TEXT NOT NULL DEFAULT 'single'
        CHECK (type IN ('single', 'album', 'ep', 'compilation', 'live')),
    genre TEXT,
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'published', 'archived')),
    release_date DATE,
    upc TEXT,
    isrc TEXT,
    streams BIGINT NOT NULL DEFAULT 0,
    revenue NUMERIC(14,2) NOT NULL DEFAULT 0,
    platforms TEXT[] NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_releases_tenant ON releases(tenant_id);
CREATE INDEX idx_releases_artist ON releases(artist_id);
ALTER TABLE releases ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS contracts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    type TEXT NOT NULL DEFAULT 'distribution_only'
        CHECK (type IN ('exclusive', 'non_exclusive', 'management', 'production', 'licensing', 'joint_venture', 'distribution_only')),
    status TEXT NOT NULL DEFAULT 'draft'
        CHECK (status IN ('draft', 'active', 'completed', 'terminated')),
    start_date TIMESTAMPTZ NOT NULL DEFAULT now(),
    end_date TIMESTAMPTZ,
    revenue_splits JSONB NOT NULL DEFAULT '{}',
    territories TEXT[] NOT NULL DEFAULT '{worldwide}',
    platforms TEXT[] NOT NULL DEFAULT '{all}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_contracts_tenant ON contracts(tenant_id);
CREATE INDEX idx_contracts_artist ON contracts(artist_id);
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;

CREATE TABLE IF NOT EXISTS revenue_entries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    contract_id UUID NOT NULL REFERENCES contracts(id) ON DELETE CASCADE,
    artist_id UUID NOT NULL REFERENCES artists(id) ON DELETE CASCADE,
    release_id UUID REFERENCES releases(id) ON DELETE SET NULL,
    amount NUMERIC(14,2) NOT NULL,
    source TEXT NOT NULL,
    split_snapshot JSONB NOT NULL DEFAULT '{}',
    artist_share NUMERIC(14,2) NOT NULL DEFAULT 0,
    label_share NUMERIC(14,2) NOT NULL DEFAULT 0,
    distributor_share NUMERIC(14,2) NOT NULL DEFAULT 0,
    manager_share NUMERIC(14,2) NOT NULL DEFAULT 0,
    producer_share NUMERIC(14,2) NOT NULL DEFAULT 0,
    recorded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_revenue_entries_tenant ON revenue_entries(tenant_id);
CREATE INDEX idx_revenue_entries_contract ON revenue_entries(contract_id);
CREATE INDEX idx_revenue_entries_artist ON revenue_entries(artist_id);
ALTER TABLE revenue_entries ENABLE ROW LEVEL SECURITY;
