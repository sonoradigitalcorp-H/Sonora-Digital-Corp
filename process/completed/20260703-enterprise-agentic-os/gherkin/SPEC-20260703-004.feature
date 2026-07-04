Feature: Enterprise Agentic OS
  Unify all services, secrets, monitoring, and agents under a single orchestrated OS

  Background:
    Given the VPS sdc-prod is accessible via SSH
    And the monorepo is at /home/ubuntu/sonora-digital-corp

  # ── M4: Secrets Encryption ──

  Scenario: age encrypts secrets files
    Given age v1.2.1 is installed
    When I run "age -r <public_key> -o file.age file"
    Then file.age is an "age encrypted file, X25519 recipient"
    And "age -d -i ~/.age/key.txt file.age" outputs the original content

  Scenario: decrypt-env.sh sources environment
    Given decrypt-env.sh exists in scripts/
    When I run "source scripts/decrypt-env.sh"
    Then ABE_TELEGRAM_TOKEN is set
    And REDIS_PASSWORD is set

  # ── M2: Nginx Gateway ──

  Scenario: No services on 0.0.0.0 except ssh and nginx
    Given the VPS is running
    When I run "ss -tlnp | awk '{print $4}' | grep '^0.0.0.0:'"
    Then the output only contains ports 22, 80, and 443

  Scenario: SSL certificates are readable by nginx
    Given /etc/letsencrypt/live/ exists
    When I run "sudo nginx -t"
    Then the output contains "syntax is ok"

  Scenario: nginx proxies to internal services
    Given nginx is running
    When I curl https://api.sonoradigitalcorp.com/
    Then the response status is 200

  # ── M1: Truth Guardian ──

  Scenario: Truth Guardian runs as systemd service
    Given truth-guardian.service is installed
    When I run "systemctl is-active truth-guardian.service"
    Then the output is "active"

  Scenario: Status API returns health of all services
    Given Truth Guardian is running
    When I curl http://127.0.0.1:8088/api/v1/status
    Then the response JSON contains "services" with all 22 services
    And each service has a status of "healthy" or "unhealthy"

  Scenario: Drift scanner detects mismatch
    Given Truth Guardian is running
    When a service is added or removed without updating TRUTH.md
    Then Truth Guardian logs a drift event
    And sends a Telegram alert

  Scenario: Compliance auditor validates CONDUCT.md
    Given Truth Guardian is running
    When the auditor runs
    Then it checks JR-Lite 15-point compliance
    And it checks Enterprise Score ≥ 60
    And it logs violations to state/quality/violations.jsonl

  # ── M3: Observability ──

  Scenario: Prometheus scrapes all targets
    Given Prometheus is configured
    When I curl http://localhost:9090/api/v1/targets
    Then all targets are in "up" state

  Scenario: Grafana dashboard is accessible
    Given Grafana is running
    When I curl http://localhost:3001/api/health
    Then the response status is 200

  Scenario: Alertmanager sends Telegram alert on failure
    Given Alertmanager is configured
    When a service becomes unhealthy
    Then a Telegram alert is sent within 60 seconds

  # ── M5: Multi-Tenant ──

  Scenario: Each tenant has isolated Qdrant collection
    Given Qdrant is running
    When I list collections via API
    Then each tenant has its own collection
    And no tenant can access another tenant's collection

  Scenario: Rate limiting per tenant
    Given the rate limiter is configured
    When a tenant exceeds its rate limit
    Then the request is rejected with HTTP 429

  # ── M6: LLM Gateway ──

  Scenario: LLM gateway routes to correct model
    Given the LLM gateway is running
    When I send a request with model=opencode-go
    Then the request is routed to the opencode-go provider
    And the response is returned

  Scenario: LLM gateway falls back on failure
    Given the primary provider is down
    When I send a request
    Then the request is routed to the fallback provider
    And the response is returned

  # ── M7: Agent Registry ──

  Scenario: Agent registry lists all agents
    Given the agent registry is running
    When I GET /api/agents
    Then the response contains all registered agents
    And each agent has a name, role, status, and health

  Scenario: Agent can be registered
    Given the agent registry is running
    When I POST /api/agents with valid agent data
    Then the agent is registered
    And the response contains the agent ID

  # ── M8: Config Unification ──

  Scenario: fleet.yml generates all configs
    Given fleet.yml is the SSOT
    When I run "python3 scripts/generate-configs.py"
    Then all service configs are regenerated
    And TRUTH.md is regenerated
