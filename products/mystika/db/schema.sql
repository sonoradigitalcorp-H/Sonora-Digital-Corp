-- ============================================================
-- Mystika Database Schema
-- Spec: SPEC-20260630-012
-- PostgreSQL
-- ============================================================

-- Create database (run as superuser)
-- CREATE DATABASE mystika WITH ENCODING 'UTF8' LC_COLLATE 'en_US.UTF-8' LC_CTYPE 'en_US.UTF-8';

-- ============================================================
-- ENUMS
-- ============================================================

CREATE TYPE user_plan AS ENUM ('free', 'mysteria', 'ritual');
CREATE TYPE payment_gateway AS ENUM ('stripe', 'mercadopago', 'crypto');
CREATE TYPE payment_status AS ENUM ('pending', 'approved', 'rejected', 'refunded', 'cancelled');
CREATE TYPE subscription_status AS ENUM ('active', 'cancelled', 'expired', 'past_due');
CREATE TYPE lesson_status AS ENUM ('draft', 'published', 'archived');
CREATE TYPE content_plan AS ENUM ('mysteria', 'ritual', 'all');
CREATE TYPE content_type AS ENUM ('photo', 'video');
CREATE TYPE instrument AS ENUM (
  'drums', 'guitar', 'bass', 'piano', 'ukulele',
  'voice', 'violin', 'saxophone', 'flute', 'production',
  'theory', 'composition'
);
CREATE TYPE notification_type AS ENUM (
  'new_lesson', 'new_content', 'live_start', 'subscription_expiring',
  'tip_received', 'message_received', 'promo', 'practice_reminder'
);

-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  telegram_id BIGINT UNIQUE,
  email TEXT UNIQUE,
  password_hash TEXT,
  username TEXT,
  first_name TEXT,
  preferred_language TEXT DEFAULT 'es' CHECK (preferred_language IN ('es', 'en')),
  plan user_plan DEFAULT 'free',
  is_admin BOOLEAN DEFAULT false,
  is_verified BOOLEAN DEFAULT false,
  age_verified BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  last_login_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'
);

CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_plan ON users(plan);

-- ============================================================
-- LESSONS (educational content)
-- ============================================================

CREATE TABLE lessons (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  instrument instrument NOT NULL,
  difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  price_mxn NUMERIC(10,2) NOT NULL DEFAULT 0,
  price_usd NUMERIC(8,2) NOT NULL DEFAULT 0,
  video_filename TEXT NOT NULL,
  video_size BIGINT,
  video_duration_seconds INT,
  thumbnail_filename TEXT,
  preview_filename TEXT, -- 30-second preview
  is_published BOOLEAN DEFAULT false,
  status lesson_status DEFAULT 'draft',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_lessons_instrument ON lessons(instrument);
CREATE INDEX idx_lessons_status ON lessons(status);
CREATE INDEX idx_lessons_published ON lessons(is_published) WHERE is_published = true;

-- ============================================================
-- COURSES (group of lessons = "Camino")
-- ============================================================

CREATE TABLE courses (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  instrument instrument,
  difficulty TEXT CHECK (difficulty IN ('beginner', 'intermediate', 'advanced')),
  price_mxn NUMERIC(10,2) DEFAULT 0,
  price_usd NUMERIC(8,2) DEFAULT 0,
  thumbnail_filename TEXT,
  is_published BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE course_lessons (
  course_id INT REFERENCES courses(id) ON DELETE CASCADE,
  lesson_id INT REFERENCES lessons(id) ON DELETE CASCADE,
  position INT NOT NULL,
  PRIMARY KEY (course_id, lesson_id)
);

-- ============================================================
-- NSFW CONTENT (gallery)
-- ============================================================

CREATE TABLE nsfw_content (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  content_type content_type NOT NULL,
  filename TEXT NOT NULL,
  file_size BIGINT,
  thumbnail_filename TEXT,
  preview_filename TEXT, -- censored/blurred preview
  min_plan content_plan NOT NULL DEFAULT 'mysteria', -- minimum plan to access
  is_published BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_nsfw_content_type ON nsfw_content(content_type);
CREATE INDEX idx_nsfw_content_plan ON nsfw_content(min_plan);
CREATE INDEX idx_nsfw_content_published ON nsfw_content(is_published) WHERE is_published = true;

-- ============================================================
-- PURCHASES (individual lesson/course purchases)
-- ============================================================

CREATE TABLE purchases (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  lesson_id INT REFERENCES lessons(id) ON DELETE SET NULL,
  course_id INT REFERENCES courses(id) ON DELETE SET NULL,
  amount_mxn NUMERIC(10,2),
  amount_usd NUMERIC(8,2),
  gateway payment_gateway NOT NULL,
  gateway_preference_id TEXT, -- MP preference ID / Stripe session ID
  gateway_payment_id TEXT, -- MP payment ID / Stripe payment intent
  status payment_status DEFAULT 'pending',
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT chk_purchase_target CHECK (
    (lesson_id IS NOT NULL AND course_id IS NULL) OR
    (lesson_id IS NULL AND course_id IS NOT NULL)
  )
);

CREATE INDEX idx_purchases_user ON purchases(user_id);
CREATE INDEX idx_purchases_status ON purchases(status);
CREATE INDEX idx_purchases_gateway ON purchases(gateway_payment_id);

-- ============================================================
-- SUBSCRIPTIONS
-- ============================================================

CREATE TABLE subscriptions (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  plan user_plan NOT NULL CHECK (plan IN ('mysteria', 'ritual')),
  gateway payment_gateway NOT NULL,
  gateway_subscription_id TEXT, -- Stripe subscription ID / MP preapproval ID
  status subscription_status DEFAULT 'active',
  current_period_start TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  current_period_end TIMESTAMPTZ NOT NULL,
  cancelled_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_status ON subscriptions(status);
CREATE INDEX idx_subscriptions_gateway ON subscriptions(gateway_subscription_id);
CREATE INDEX idx_subscriptions_active ON subscriptions(user_id) WHERE status = 'active';

-- ============================================================
-- TIPS / DONATIONS ("Ofrendas")
-- ============================================================

CREATE TABLE tips (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  amount_mxn NUMERIC(10,2),
  amount_usd NUMERIC(8,2),
  gateway payment_gateway NOT NULL,
  gateway_payment_id TEXT,
  message TEXT, -- message to Lilith
  is_public BOOLEAN DEFAULT true, -- show on public offering wall
  status payment_status DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_tips_user ON tips(user_id);
CREATE INDEX idx_tips_public ON tips(is_public) WHERE is_public = true AND status = 'approved';

-- ============================================================
-- E-COMMERCE (Mystika Apparel)
-- ============================================================

CREATE TABLE shop_products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  price_mxn NUMERIC(10,2) NOT NULL,
  price_usd NUMERIC(8,2) NOT NULL,
  images TEXT[] DEFAULT '{}',
  sizes TEXT[] DEFAULT '{}',
  colors TEXT[] DEFAULT '{}',
  stock INT DEFAULT 0,
  is_available BOOLEAN DEFAULT true,
  is_featured BOOLEAN DEFAULT false,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE shop_orders (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  total_mxn NUMERIC(10,2) NOT NULL,
  total_usd NUMERIC(8,2) NOT NULL,
  shipping_address JSONB,
  gateway payment_gateway NOT NULL,
  gateway_payment_id TEXT,
  status payment_status DEFAULT 'pending',
  tracking_number TEXT,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE shop_order_items (
  id SERIAL PRIMARY KEY,
  order_id INT NOT NULL REFERENCES shop_orders(id) ON DELETE CASCADE,
  product_id INT NOT NULL REFERENCES shop_products(id),
  quantity INT NOT NULL DEFAULT 1,
  size TEXT,
  color TEXT,
  unit_price_mxn NUMERIC(10,2) NOT NULL,
  unit_price_usd NUMERIC(8,2) NOT NULL
);

-- ============================================================
-- ACCESS TOKENS (for video streaming)
-- ============================================================

CREATE TABLE access_tokens (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  lesson_id INT REFERENCES lessons(id) ON DELETE CASCADE,
  nsfw_content_id INT REFERENCES nsfw_content(id) ON DELETE CASCADE,
  token TEXT UNIQUE NOT NULL,
  max_views INT DEFAULT 1, -- how many times can watch before consumed (1 = ephemeral, -1 = unlimited)
  view_count INT DEFAULT 0,
  is_retained BOOLEAN DEFAULT false, -- true if user paid to retain
  expires_at TIMESTAMPTZ NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT chk_access_target CHECK (
    (lesson_id IS NOT NULL AND nsfw_content_id IS NULL) OR
    (lesson_id IS NULL AND nsfw_content_id IS NOT NULL)
  )
);

CREATE INDEX idx_access_tokens_token ON access_tokens(token);
CREATE INDEX idx_access_tokens_user ON access_tokens(user_id);

-- ============================================================
-- CONTENT RETENTION ("Memoria" — pay to keep)
-- ============================================================

CREATE TABLE content_retentions (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  lesson_id INT REFERENCES lessons(id) ON DELETE CASCADE,
  nsfw_content_id INT REFERENCES nsfw_content(id) ON DELETE CASCADE,
  gateway payment_gateway NOT NULL,
  gateway_payment_id TEXT,
  amount_mxn NUMERIC(10,2) NOT NULL,
  amount_usd NUMERIC(8,2) NOT NULL,
  retention_type TEXT NOT NULL CHECK (retention_type IN ('retain', 'download')),
  download_url TEXT, -- temporary download link (if retention_type = 'download')
  download_expires_at TIMESTAMPTZ, -- download link expiry
  watermark TEXT, -- watermark string applied to downloaded file
  status payment_status DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  CONSTRAINT chk_retention_target CHECK (
    (lesson_id IS NOT NULL AND nsfw_content_id IS NULL) OR
    (lesson_id IS NULL AND nsfw_content_id IS NOT NULL)
  )
);

CREATE INDEX idx_content_retentions_user ON content_retentions(user_id);
CREATE INDEX idx_content_retentions_status ON content_retentions(status);

-- ============================================================
-- AI CHAT (conversations with Lilith)
-- ============================================================

CREATE TABLE chat_messages (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
  content TEXT NOT NULL,
  tokens_used INT,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_chat_user ON chat_messages(user_id);
CREATE INDEX idx_chat_created ON chat_messages(created_at);

-- Daily message count per user (for Mysteria plan limit)
CREATE TABLE chat_usage (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  date DATE NOT NULL DEFAULT CURRENT_DATE,
  message_count INT DEFAULT 0,
  UNIQUE (user_id, date)
);

-- ============================================================
-- LIVE STREAMS ("Aquelarres")
-- ============================================================

CREATE TABLE live_events (
  id SERIAL PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  scheduled_at TIMESTAMPTZ NOT NULL,
  ended_at TIMESTAMPTZ,
  stream_url TEXT,
  recording_filename TEXT,
  min_plan user_plan NOT NULL DEFAULT 'mysteria',
  status TEXT DEFAULT 'scheduled' CHECK (status IN ('scheduled', 'live', 'ended', 'cancelled')),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_live_events_status ON live_events(status);
CREATE INDEX idx_live_events_scheduled ON live_events(scheduled_at) WHERE status = 'scheduled';

-- ============================================================
-- NOTIFICATIONS ("Susurros")
-- ============================================================

CREATE TABLE notifications (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  type notification_type NOT NULL,
  title TEXT NOT NULL,
  body TEXT,
  data JSONB DEFAULT '{}',
  is_read BOOLEAN DEFAULT false,
  sent_via_push BOOLEAN DEFAULT false,
  sent_via_telegram BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id, is_read);

-- Firebase push tokens
CREATE TABLE push_tokens (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token TEXT NOT NULL,
  platform TEXT CHECK (platform IN ('ios', 'android', 'web')),
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_push_tokens_token ON push_tokens(token);

-- ============================================================
-- STUDENT PROGRESS
-- ============================================================

CREATE TABLE lesson_progress (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  watched_seconds INT DEFAULT 0,
  is_completed BOOLEAN DEFAULT false,
  completed_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (user_id, lesson_id)
);

CREATE TABLE assignments (
  id SERIAL PRIMARY KEY,
  lesson_id INT NOT NULL REFERENCES lessons(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  due_days INT, -- days after lesson completion
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE assignment_submissions (
  id SERIAL PRIMARY KEY,
  assignment_id INT NOT NULL REFERENCES assignments(id) ON DELETE CASCADE,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  submission_text TEXT,
  audio_filename TEXT,
  video_filename TEXT,
  feedback_text TEXT, -- Lilith's feedback
  feedback_read BOOLEAN DEFAULT false,
  score INT CHECK (score >= 0 AND score <= 100),
  submitted_at TIMESTAMPTZ DEFAULT NOW(),
  feedback_at TIMESTAMPTZ,
  UNIQUE (assignment_id, user_id)
);

-- ============================================================
-- AUDIT LOG
-- ============================================================

CREATE TABLE audit_log (
  id SERIAL PRIMARY KEY,
  user_id INT REFERENCES users(id),
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id INT,
  details JSONB DEFAULT '{}',
  ip_address INET,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_log_user ON audit_log(user_id);
CREATE INDEX idx_audit_log_action ON audit_log(action);
CREATE INDEX idx_audit_log_created ON audit_log(created_at);

-- Auto-invalidate token when view_count reaches max_views
CREATE OR REPLACE FUNCTION check_token_consumed()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.max_views > 0 AND NEW.view_count >= NEW.max_views THEN
    NEW.expires_at = NOW();
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_access_tokens_consumed
  BEFORE UPDATE OF view_count ON access_tokens
  FOR EACH ROW
  WHEN (OLD.view_count IS DISTINCT FROM NEW.view_count)
  EXECUTE FUNCTION check_token_consumed();

-- ============================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_lessons_updated_at
  BEFORE UPDATE ON lessons
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_courses_updated_at
  BEFORE UPDATE ON courses
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_purchases_updated_at
  BEFORE UPDATE ON purchases
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_subscriptions_updated_at
  BEFORE UPDATE ON subscriptions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_shop_products_updated_at
  BEFORE UPDATE ON shop_products
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

CREATE TRIGGER trg_shop_orders_updated_at
  BEFORE UPDATE ON shop_orders
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();

-- Auto-update user.plan when subscription status changes
CREATE OR REPLACE FUNCTION update_user_plan_on_subscription()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'active' THEN
    UPDATE users SET plan = NEW.plan WHERE id = NEW.user_id;
  ELSIF NEW.status IN ('cancelled', 'expired') THEN
    -- Only downgrade if no other active subscription
    IF NOT EXISTS (
      SELECT 1 FROM subscriptions
      WHERE user_id = NEW.user_id AND status = 'active' AND id != NEW.id
    ) THEN
      UPDATE users SET plan = 'free' WHERE id = NEW.user_id;
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_subscription_plan_update
  AFTER INSERT OR UPDATE OF status ON subscriptions
  FOR EACH ROW EXECUTE FUNCTION update_user_plan_on_subscription();

-- Auto-update user.plan on purchase (if buying unlocks a plan level)
CREATE OR REPLACE FUNCTION update_user_plan_on_purchase()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.status = 'approved' AND NEW.lesson_id IS NOT NULL THEN
    -- Individual lesson purchases don't change plan
    NULL;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================
-- SEED DATA
-- ============================================================

-- Admin user (Lilith herself)
INSERT INTO users (telegram_id, email, username, first_name, is_admin, is_verified, age_verified)
VALUES (NULL, 'lilith@mystika.app', 'lilith', 'Lilith Mystika', true, true, true);

-- Sample instruments for catalog filtering
INSERT INTO lessons (title, description, instrument, difficulty, price_mxn, price_usd, video_filename, is_published, status)
VALUES
  ('Bienvenido a Mystika', 'Tu primer ritual musical. Conoce a Lilith y prepárate para el viaje.', 'drums', 'beginner', 0, 0, 'welcome.mp4', true, 'published'),
  ('Ritmos Fundamentales', 'Los patrones de batería que todo baterista debe dominar.', 'drums', 'beginner', 299, 14.99, 'basic-rythms.mp4', true, 'published'),
  ('Acordes que Encienden', 'Tus primeros acordes en guitarra. Siente la vibración.', 'guitar', 'beginner', 299, 14.99, 'first-chords.mp4', false, 'draft');
