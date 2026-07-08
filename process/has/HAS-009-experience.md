# HAS-009 — Hermes Architecture Standard: Experience Layer

**Status:** Draft v1
**Domain:** ux
**Updated:** 2026-07-08
**Depends on:** HAS-000, HAS-004

---

## 1. Purpose

Define the contract between Hermes Kernel and user-facing experiences. The UI is not "pages" — it is **states** represented by the Orb. The Experience Layer is channel-agnostic: same kernel serves Web, Voice, Telegram, CLI, API.

---

## 2. Orb States

The Orb is the primary visual representation of Hermes. It has 6 states:

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ IDLE     │→│LISTENING │→│THINKING  │→│EXECUTING │→│COMPLETED │→│ IDLE     │
│ (dim     │  │(pulse    │  │(spin     │  │(progress │  │(glow     │  │          │
│  white)  │  │ blue)    │  │ purple)  │  │ bar)     │  │ green)   │  │          │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
                                                              │
                                                         ┌────▼────┐
                                                         │ ALERT   │
                                                         │ (red    │
                                                         │  pulse) │
                                                         └─────────┘
```

| State | Visual | Audio | Description |
|---|---|---|---|
| `IDLE` | Dim white sphere | Silence | Waiting for input |
| `LISTENING` | Pulsing blue | Mic active | User speaking/typing |
| `THINKING` | Rotating purple | Soft hum | Kernel processing |
| `EXECUTING` | Progress arc | Tick sound | Task being executed |
| `COMPLETED` | Glowing green | Success chime | Task done |
| `ALERT` | Pulsing red | Alert tone | Error or attention needed |

---

## 3. Experience Channels

| Channel | Protocol | State feedback | Priority |
|---|---|---|---|
| **Web** | WebSocket + REST | Full Orb + audio | Primary |
| **Voice** | WebRTC / Twilio | Audio tones only | Real-time |
| **Telegram** | Bot API | Text + emoji | Async |
| **WhatsApp** | Twilio API | Text + emoji | Async |
| **CLI** | stdin/stdout | ASCII spinner | Dev |
| **API** | HTTP/REST | Status in response | Integration |

---

## 4. Kernel → Experience Contract

The Kernel never knows which channel it's serving. It outputs structured messages:

```json
{
  "type": "orb.state",
  "state": "thinking",
  "message": "Analyzing artist data...",
  "progress": null,
  "actions": [],
  "metadata": {
    "agent": "research-agent",
    "capability": "analyze-artist",
    "duration_ms": 0
  }
}
```

```json
{
  "type": "orb.state",
  "state": "executing",
  "message": "Generating video...",
  "progress": 45,
  "actions": [
    {"id": "cancel", "label": "Cancel"},
    {"id": "priority-up", "label": "Speed up"}
  ],
  "metadata": {
    "agent": "video-agent",
    "capability": "generate-video",
    "duration_ms": 3240
  }
}
```

```json
{
  "type": "orb.state",
  "state": "completed",
  "message": "Video generated successfully",
  "progress": 100,
  "actions": [
    {"id": "view", "label": "View video"},
    {"id": "share", "label": "Share"}
  ],
  "metadata": {
    "agent": "video-agent",
    "capability": "generate-video",
    "duration_ms": 12450,
    "output": {"url": "https://...", "format": "mp4", "duration": 30}
  }
}
```

---

## 5. Experience Stack (Web)

| Layer | Technology | Purpose |
|---|---|---|
| Framework | SvelteKit | SSR + routing + WebSocket |
| 3D | Threlte (Svelte + Three.js) | Orb rendering |
| Animation | Theatre.js | Orb state transitions |
| Voice | Web Speech API + Whisper | Voice input/output |
| Styling | Tailwind + Motion | UI + animations |
| Real-time | WebSocket | Kernel communication |

---

## 6. Directory Structure

```
experience/
├── web/                           # SvelteKit web app
│   ├── src/
│   │   ├── routes/
│   │   ├── components/
│   │   │   ├── orb/
│   │   │   │   ├── Orb.svelte
│   │   │   │   ├── states/
│   │   │   │   │   ├── Idle.svelte
│   │   │   │   │   ├── Listening.svelte
│   │   │   │   │   ├── Thinking.svelte
│   │   │   │   │   ├── Executing.svelte
│   │   │   │   │   ├── Completed.svelte
│   │   │   │   │   └── Alert.svelte
│   │   │   │   └── animations.ts
│   │   │   ├── chat/
│   │   │   ├── dashboard/
│   │   │   └── canvas/
│   │   ├── lib/
│   │   │   ├── kernel-client.ts   # WebSocket client to Kernel
│   │   │   └── orb-machine.ts     # State machine
│   │   └── app.html
│   ├── package.json
│   └── svelte.config.js
├── voice/                         # Voice experience
├── telegram/                      # Telegram bot (existing)
└── cli/                           # CLI client
```

---

## 7. Events

| Event | Trigger | Payload |
|---|---|---|
| `experience.orb.state_changed` | Orb transition | `{ from, to, session_id }` |
| `experience.user.input` | User interaction | `{ channel, input_type, length }` |
| `experience.error` | Channel error | `{ channel, error }` |

---

## 8. Success Criteria

- [ ] Orb has 6 visual states (Idle → Listening → Thinking → Executing → Completed → Alert)
- [ ] Kernel outputs structured orb.state messages (not raw text)
- [ ] Web experience connects via WebSocket to Kernel
- [ ] All channels (web, voice, telegram, cli) consume same Kernel output
- [ ] Orb transitions animate smoothly (Theatre.js)
- [ ] Experience errors don't crash Kernel
