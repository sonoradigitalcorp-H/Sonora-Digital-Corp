# ADR-20260802-JARVIS-PROACTIVE

**Title:** JARVIS Proactive Engine  
**Date:** 2026-08-02  
**Status:** accepted

## Context

JARVIS was initially reactive only. The microphone was toggle-based (manual start/stop), there was no Playwright browser integration, and no web search capability. Users had to explicitly trigger every interaction, limiting the assistant's utility for proactive tasks like monitoring, automated browsing, and real-time information retrieval.

## Decision

Create a proactive JARVIS engine with:
- Continuous microphone listening with wake word detection
- Intent classification for 10+ action types
- Action routing to appropriate handlers
- Playwright browser integration for web automation
- Inline screenshot capture and display
- Unlimited context via engram/postgres/rag/redis
- Confirmation flows for destructive actions
- Direct audio output
- Hermes MCP integration
- Web search capabilities

## Options Considered

1. **Keep reactive (status quo):** Minimal effort but limited functionality. Users must manually trigger all interactions.
2. **Make proactive:** More complex architecture but enables autonomous actions, real-time monitoring, and hands-free operation.

## Consequences

- JARVIS can now take autonomous actions (open pages, create dashboards, query databases)
- Browser automation enables web monitoring and data extraction
- Continuous mic enables hands-free operation
- More complex state management required
- Higher resource usage due to persistent processes
- Improved user experience for repetitive tasks

## Related

- ADR-20260802-SDC-SYSTEM-SESSION
- SPEC-023 through SPEC-029