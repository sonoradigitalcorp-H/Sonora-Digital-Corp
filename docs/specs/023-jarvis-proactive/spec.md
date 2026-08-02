# SPEC-023: JARVIS Proactive Engine

## Objective

JARVIS proactivo con mic continuo, wake word, acciones reales

## Tier

3

## Functional Requirements

### FR1: Continuous Microphone
JARVIS maintains continuous microphone listening with low-resource audio processing.

### FR2: Wake Word Detection
System detects configurable wake words (e.g., "Hey JARVIS") to activate processing.

### FR3: Intent Classification (10+ Intents)
JARVIS classifies user intent into 10+ categories including:
- Web search
- Browser automation
- Database queries
- Dashboard creation
- System monitoring
- Content creation
- Communication
- File operations
- Data analysis
- Task automation

### FR4: Playwright Browser Integration
Full Playwright browser control for web navigation, form filling, and automation.

### FR5: Inline Screenshots
Capture and display screenshots directly in chat responses.

### FR6: Unlimited Context
Access unlimited context via engram memory, PostgreSQL, RAG, and Redis.

### FR7: Destructive Action Confirmation
Confirmation flows for destructive actions (delete, overwrite, send, etc.).

### FR8: Direct Audio Output
Text-to-speech audio responses directly to user.

### FR9: Hermes MCP Integration
Connect to Hermes gateway via HTTP MCP for external service integration.

### FR10: Web Search
Integrated web search capability for real-time information retrieval.

## Score

85/100

## Implementation Notes

- Uses existing MCP infrastructure (sdc-mcp-local, playwright)
- Integrates with engram memory system
- Leverages Qdrant for RAG capabilities
- Redis for session state and caching
- PostgreSQL for persistent data storage