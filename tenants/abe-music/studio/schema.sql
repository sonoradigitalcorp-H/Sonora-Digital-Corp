-- ABE Studio — Database Schema
-- Sigue el patrón de 008_abe_music_hub.sql
-- En producción, estas tablas van en HERMES OS PostgreSQL
-- En desarrollo, se crean en SQLite local

CREATE TABLE IF NOT EXISTS studio_artists (
    id TEXT PRIMARY KEY,
    artist_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    genre TEXT,
    character_refs JSONB DEFAULT '[]',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS studio_tasks (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id INTEGER NOT NULL DEFAULT 0,
    artist_id TEXT,
    task_type TEXT NOT NULL CHECK(task_type IN ('text-to-video','image-to-video','reference-to-video')),
    model TEXT DEFAULT 'seedance-2-0',
    seedance_task_id TEXT,
    status TEXT DEFAULT 'queued' CHECK(status IN ('queued','generating','completed','failed')),
    billing_status TEXT DEFAULT 'reserved' CHECK(billing_status IN ('reserved','charged','refunded')),
    credits INTEGER DEFAULT 0,
    prompt TEXT,
    image_urls TEXT DEFAULT '[]',
    audio_urls TEXT DEFAULT '[]',
    video_urls TEXT DEFAULT '[]',
    duration INTEGER DEFAULT 5,
    aspect_ratio TEXT DEFAULT '9:16',
    resolution TEXT DEFAULT '720p',
    generate_audio INTEGER DEFAULT 1,
    result_url TEXT,
    thumbnail_url TEXT,
    result_expires_at TEXT,
    processing_time INTEGER,
    failed_reason TEXT,
    callback_url TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    completed_at TEXT,
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS studio_usage (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    user_id INTEGER NOT NULL,
    month TEXT NOT NULL DEFAULT (strftime('%Y-%m-01', 'now')),
    reels_generated INTEGER DEFAULT 0,
    credits_consumed INTEGER DEFAULT 0,
    UNIQUE(user_id, month)
);

CREATE TABLE IF NOT EXISTS studio_templates (
    id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
    name TEXT NOT NULL,
    prompt TEXT NOT NULL,
    category TEXT,
    artist_id TEXT,
    is_public INTEGER DEFAULT 0,
    created_by INTEGER,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON studio_tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_user ON studio_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_tasks_created ON studio_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_usage_user_month ON studio_usage(user_id, month);
