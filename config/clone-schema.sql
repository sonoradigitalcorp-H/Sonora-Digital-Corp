-- Clone Service Database Schema (SQLite)
-- Almacena clientes, fotos, audio, modelos entrenados, assets generados y créditos.

CREATE TABLE IF NOT EXISTS clients (
    id TEXT PRIMARY KEY,
    status TEXT DEFAULT 'pending',
    pack_type TEXT,
    credits_photo INTEGER DEFAULT 0,
    credits_video INTEGER DEFAULT 0,
    credits_tts INTEGER DEFAULT 0,
    credits_training INTEGER DEFAULT 0,
    lora_id TEXT,
    voice_id TEXT,
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    url TEXT NOT NULL,
    validated INTEGER DEFAULT 0,
    has_face INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS audio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    url TEXT NOT NULL,
    validated INTEGER DEFAULT 0,
    duration_s REAL DEFAULT 0,
    snr_db REAL DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id TEXT NOT NULL,
    type TEXT NOT NULL,
    url TEXT NOT NULL,
    prompt TEXT,
    credits_used INTEGER DEFAULT 0,
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

-- Índices para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_photos_client ON photos(client_id);
CREATE INDEX IF NOT EXISTS idx_audio_client ON audio(client_id);
CREATE INDEX IF NOT EXISTS idx_assets_client ON assets(client_id);
CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
