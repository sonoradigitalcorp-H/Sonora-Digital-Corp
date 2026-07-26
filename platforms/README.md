# Platforms — Continuity Bridge Integration

This module provides a shared `ContinuityBridge` that all 4 channels (Telegram, WhatsApp, Web, Voice) import to maintain unified session context.

## Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Telegram   │  │   WhatsApp   │  │     Web      │  │    Voice    │
│    Bot       │  │   Bridge     │  │   FastAPI    │  │   STT/TTS   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                  │                 │
       └─────────────────┴──────────────────┴─────────────────┘
                              │
                    ┌─────────▼─────────┐
                    │ ContinuityBridge  │
                    │ (platforms/       │
                    │  continuity_      │
                    │  bridge.py)       │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │ SessionOrchestrator│
                    │ (src/core/        │
                    │  session_         │
                    │  orchestrator.py)  │
                    └─────────┬─────────┘
                              │
                    ┌─────────▼─────────┐
                    │  Engram (SQLite)   │
                    │  + MemSabe        │
                    └───────────────────┘
```

## Integration Guide

### 1. Telegram Bot Integration

In your Telegram bot message handler:

```python
from platforms.continuity_bridge import ContinuityBridge

bridge = ContinuityBridge()

async def handle_message(update, context):
    user_id = str(update.effective_user.id)

    # Get cross-channel context (includes WhatsApp, Web, Voice history)
    ctx = bridge.get_context(user_id, "telegram")
    unified_id = ctx["unified_user_id"]

    # Process message with unified context
    response = await process_with_context(update.message.text, ctx)

    # Save interaction to unified memory
    bridge.save_interaction(user_id, "telegram", update.message.text, response)

    await update.message.reply_text(response)
```

### 2. WhatsApp Bridge Integration

In your WhatsApp message handler:

```python
from platforms.continuity_bridge import ContinuityBridge

bridge = ContinuityBridge()

def handle_whatsapp_message(phone_number, message_text):
    # Get cross-channel context (includes Telegram, Web, Voice history)
    ctx = bridge.get_context(phone_number, "whatsapp")

    # Process with unified context
    response = process_message(message_text, ctx)

    # Save interaction
    bridge.save_interaction(phone_number, "whatsapp", message_text, response)

    return response
```

### 3. Web UI Integration

Already available via the FastAPI endpoints:

```python
# GET /api/continuity/{user_id}?channel=web
# POST /api/continuity/link
# GET /api/continuity/{user_id}/history?channels=telegram,whatsapp
```

### 4. Voice Channel Integration

```python
from platforms.continuity_bridge import ContinuityBridge

bridge = ContinuityBridge()

def handle_voice_interaction(voice_user_id, transcribed_text):
    ctx = bridge.get_context(voice_user_id, "voice")
    response = process_with_context(transcribed_text, ctx)
    bridge.save_interaction(voice_user_id, "voice", transcribed_text, response)
    return response
```

## Identity Linking

To link a user's identities across channels:

**Via CLI:**
```bash
python3 scripts/link-identity.py --telegram 12345 --whatsapp +521555010203
python3 scripts/link-identity.py --web user@email.com --telegram 12345
```

**Via API:**
```bash
curl -X POST "http://localhost:5174/api/continuity/link?primary=12345&secondary=%2B521555010203&primary_channel=telegram&secondary_channel=whatsapp"
```

**Programmatically:**
```python
from platforms.continuity_bridge import ContinuityBridge

bridge = ContinuityBridge()
bridge.link_identities("12345", "+521555010203", "telegram", "whatsapp")
```

## Key Concepts

- **Unified User ID**: UUID that identifies a user across all channels
- **Identity Linking**: Mapping channel-specific IDs to a single unified ID
- **Cross-Channel Context**: Session context that includes history from all channels
- **Session Timeout**: Inactive sessions are cleaned up after 30 minutes
- **Memory Layers**:
  - `working` — active interaction state
  - `customer` — user identity links, preferences, long-term context

## Configuration

The bridge uses Engram (SQLite with FTS5) for persistence. MemSabe provides the cross-channel reasoning layer.

No additional configuration is required — the bridge auto-initializes with the default Engram instance.
