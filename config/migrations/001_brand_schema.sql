-- ============================================================
-- SDC Platform — Schema completo
-- Ejecutar en Supabase SQL Editor
-- ============================================================

-- Users are managed by Supabase Auth (Google OAuth)

-- Agent metrics (inserted by Hermes Agent / Ops Agent)
CREATE TABLE IF NOT EXISTS agent_metrics (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  agent_name  TEXT NOT NULL,
  status      TEXT DEFAULT 'operational',
  calls_today INT DEFAULT 0,
  leads_scored INT DEFAULT 0,
  avg_duration_sec FLOAT DEFAULT 0,
  latency_ms  FLOAT DEFAULT 0,
  created_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE agent_metrics ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own metrics"
  ON agent_metrics FOR SELECT
  USING (auth.uid() = user_id);

-- Agent events (real-time log)
CREATE TABLE IF NOT EXISTS agent_events (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id     UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  event_type  TEXT NOT NULL,
  payload     JSONB DEFAULT '{}',
  severity    TEXT DEFAULT 'info',
  created_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE agent_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own events"
  ON agent_events FOR SELECT
  USING (auth.uid() = user_id);

-- Service status (public read, admin write)
CREATE TABLE IF NOT EXISTS service_status (
  id          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name        TEXT NOT NULL UNIQUE,
  status      TEXT DEFAULT 'operational',
  latency_ms  FLOAT DEFAULT 0,
  last_checked TIMESTAMPTZ DEFAULT now(),
  updated_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE service_status ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Public read service status"
  ON service_status FOR SELECT
  USING (true);

-- User profiles
CREATE TABLE IF NOT EXISTS user_profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  email       TEXT,
  full_name   TEXT,
  company     TEXT,
  plan        TEXT DEFAULT 'free',
  created_at  TIMESTAMPTZ DEFAULT now()
);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users see own profile"
  ON user_profiles FOR SELECT
  USING (auth.uid() = id);

-- Insert default service statuses
INSERT INTO service_status (name, status) VALUES
  ('AI Call Engine', 'operational'),
  ('Clone Service', 'operational'),
  ('WhatsApp Agent', 'operational'),
  ('Hermes Gateway', 'operational'),
  ('Neo4j Graph DB', 'operational'),
  ('Qdrant Vector', 'operational'),
  ('Event Bus', 'operational'),
  ('RabbitMQ', 'operational')
ON CONFLICT (name) DO NOTHING;
