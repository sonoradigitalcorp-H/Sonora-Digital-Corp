-- CRM Unified Schema — Sonora Digital Corp
-- SQLite schema for leads, contacts, interactions, calls, deals

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    company TEXT,
    role TEXT,
    source TEXT DEFAULT 'manual',  -- manual, whatsapp, telegram, web, referral
    lead_type TEXT DEFAULT 'cold', -- cold, warm, hot
    lead_score REAL DEFAULT 0.0,
    tags TEXT DEFAULT '[]',        -- JSON array
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    channel TEXT NOT NULL,         -- whatsapp, telegram, voice, email, sms, web
    direction TEXT NOT NULL,       -- inbound, outbound
    content TEXT,                  -- message text or transcription
    media_type TEXT,               -- text, audio, image, video, document
    media_url TEXT,                -- local path or URL to media file
    duration_seconds REAL,         -- for voice/audio
    sentiment TEXT,                -- positive, neutral, negative
    agent TEXT,                    -- which AI agent handled this
    raw_data TEXT,                 -- JSON blob of original message
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    direction TEXT NOT NULL,       -- inbound, outbound
    duration_seconds REAL,
    recording_url TEXT,            -- local path to audio file
    transcript TEXT,               -- full transcription
    summary TEXT,                  -- AI-generated summary
    sentiment TEXT,
    outcome TEXT,                  -- connected, voicemail, no_answer, busy
    agent TEXT,
    started_at DATETIME,
    ended_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS deals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    value REAL DEFAULT 0.0,
    currency TEXT DEFAULT 'USD',
    stage TEXT DEFAULT 'prospecting', -- prospecting, qualification, proposal, negotiation, closed_won, closed_lost
    probability REAL DEFAULT 0.0,
    expected_close DATE,
    actual_close DATE,
    lost_reason TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS activity_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    contact_id INTEGER,
    deal_id INTEGER,
    action TEXT NOT NULL,          -- created, updated, interacted, called, emailed, deal_stage_changed
    description TEXT,
    metadata TEXT,                 -- JSON blob
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE SET NULL,
    FOREIGN KEY (deal_id) REFERENCES deals(id) ON DELETE SET NULL
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_lead_type ON contacts(lead_type);
CREATE INDEX IF NOT EXISTS idx_interactions_contact ON interactions(contact_id);
CREATE INDEX IF NOT EXISTS idx_interactions_channel ON interactions(channel);
CREATE INDEX IF NOT EXISTS idx_interactions_created ON interactions(created_at);
CREATE INDEX IF NOT EXISTS idx_calls_contact ON calls(contact_id);
CREATE INDEX IF NOT EXISTS idx_deals_contact ON deals(contact_id);
CREATE INDEX IF NOT EXISTS idx_deals_stage ON deals(stage);
CREATE INDEX IF NOT EXISTS idx_activity_contact ON activity_log(contact_id);
