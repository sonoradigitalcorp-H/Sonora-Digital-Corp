Feature: Consolidación del Ecosistema Hermes en VPS Hostinger
  As a developer (MYSTIC/SDC)
  I want the VPS Hostinger to be the single source of truth for Hermes
  So that memory, bots, and orchestration are unified and reliable

  Background:
    Given the VPS Hostinger "45.90.108.12" is accessible via SSH
    And the VPS has Docker Compose running at "/opt/sdc"
    And the laptop has RAM "3.3GB" and should run no heavy processes

  # ── FASE 1: VPS como Fuente Canónica ──────────────────────────────

  Scenario: VPS gateway is the only active Hermes instance
    Given the VPS gateway "sdc-hermes" container is running
    When I check the VPS health endpoint "http://127.0.0.1:8642/health"
    Then the response is HTTP 200

  Scenario: Local gateway is shut down after migration
    Given the local gateway process was running on port 8642
    When I run "systemctl --user stop hermes-gateway" on the laptop
    Then no Hermes gateway process is listening on local port 8642
    And "ps aux | grep hermes" on local shows 0 gateway processes

  Scenario: VPS is the only Telegram polling instance
    Given the VPS has Telegram bots configured in config.yaml
    When I check Telegram bot status for "sonora-digital-corp"
    Then the bot responds to getMe without error
    And there is only one polling process per bot

  # ── FASE 2: Token Tu-Bandera + Polling Fix ────────────────────────

  Scenario: Tu-Bandera token is stored securely in env file
    Given the new token is provided by the Jefe
    When I save it to "/opt/sdc/hermes-data/.env" as "TU_BANDERA_TOKEN"
    Then the file permissions are 600
    And the config.yaml references "${TU_BANDERA_TOKEN}" (not hardcoded)

  Scenario: Tu-Bandera bot is active and responding
    Given the token is correctly configured
    When I call Telegram getMe for the tu-bandera bot
    Then the bot username is "TBasistente_bot"
    And the bot is not in error state

  Scenario: No double polling conflict
    Given both local and VPS had Telegram enabled
    When I check all Telegram polling processes across both machines
    Then each bot token has exactly one polling process
    And there is no 409 Conflict error in logs

  # ── FASE 3: Fusión de Memorias ────────────────────────────────────

  Scenario: Memory backups exist before consolidation
    Given the local memory_store.db has 4 facts
    And the VPS memory_store.db has 5 facts
    When I create backups to "/tmp/hermes_backup_YYYYMMDD/"
    Then backup files exist for both memory_store.db and engram.db
    And each backup is verified (non-zero, readable)

  Scenario: Engram becomes the single memory source
    Given backups exist and are verified
    When I migrate facts from both memory_store.db to Engram
    Then "engram stats" shows observations >= 810
    And both old memory_store.db are archived (not deleted)

  Scenario: Qdrant has vector collections in VPS
    Given Qdrant is running on VPS port 6333
    When I check "/collections" endpoint
    Then at least 2 collections exist (engram_memories, tubandera_kb)
    And each collection has points_count > 0

  Scenario: Hermes VPS uses Engram for memory
    Given Engram is running on VPS port 7437
    When I check config.yaml memory settings
    Then memory_enabled is true
    And the vector store points to Qdrant localhost:6333

  Scenario: Factual memory recall works end-to-end
    Given memory has been consolidated in Engram
    When I ask Hermes VPS "what is the name of the Tu Bandera founder"
    Then the response contains "Roberto" (or equivalent factual answer)
    And the response is generated in under 5 seconds

  # ── FASE 4: Limpieza opencode.db ──────────────────────────────────

  Scenario: opencode.db backup exists before cleanup
    Given opencode.db is 2.2GB with 345K events
    When I create backup to "/tmp/opencode_backup_YYYYMMDD/"
    Then the backup file exists and is non-zero
    And "sqlite3 <backup> pragma integrity_check" returns "ok"

  Scenario: Old events are purged and DB shrinks
    Given the backup is verified
    When I delete events older than 30 days and run VACUUM
    Then "ls -lh opencode.db" shows size <= 300 MB
    And "pragma integrity_check" returns "ok"
    And at least 10 sessions remain

  Scenario: OpenCode works correctly after cleanup
    Given the DB has been cleaned and vacuumed
    When I open opencode and start a new session
    Then the session creates normally
    And I can read past sessions without error
    And the DB does not grow beyond 300 MB in 1 hour of use

  # ── FASE 5: Estabilidad Gateway (si aplica) ──────────────────────

  Scenario: Gateway local survives 24h without RAM crash (if kept)
    Given the local gateway is running with memory limits
    When 24 hours pass with moderate usage
    Then no exit_nonzero appears in gateway logs
    And "free -m" shows available RAM > 200MB throughout

  Scenario: MCP hermes-agents connects without errors
    Given the gateway is running
    When I check logs for "hermes-agents" for 1 hour
    Then zero "failed initial connection" warnings appear
    And the MCP server stays in "connected" state

  # ── VALIDACIONES GLOBALES ────────────────────────────────────────

  Scenario: Web presence is intact after all changes
    Given all phases are complete
    When I curl "https://sonoradigitalcorp.com/"
    Then HTTP response is 200
    And the page title contains "Sonora Digital Corp"

  Scenario: Tubandera web is intact after all changes
    Given all phases are complete
    When I curl "https://tubandera.online/"
    Then HTTP response is 200
    And the page title contains "Tu Bandera"

  Scenario: No secrets in git repository
    Given all config changes are committed
    When I run "git grep -rnE 'sk-or-[a-zA-Z0-9]{20,}|BOT_TOKEN=|API_KEY='"
    Then zero matches are found in tracked files
    And all secrets are in .env files outside git
