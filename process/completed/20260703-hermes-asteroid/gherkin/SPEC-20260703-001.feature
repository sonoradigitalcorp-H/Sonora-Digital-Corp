Feature: Hermes Asteroid Unification
  As a system architect
  I want to unify all services on VPS sdc-prod
  So that laptop is a thin client and infra is centralized

  Background:
    Given SSH access to both machines
    And sudo access on laptop

  Scenario: Diagnose real architecture
    Given the assumption is dual-server architecture
    When I run `ss -tlnp`, `ps aux`, and `docker ps` on both machines
    Then I discover VPS has 11GB RAM (load 0.15) vs laptop 3.2GB RAM (load 9.24)
    And I discover laptop runs duplicate OpenClaw, Hermes, and Docker containers

  Scenario: Kill duplicate services on laptop
    Given laptop has duplicate OpenClaw (PID 848) with Restart=always
    When I override systemd unit with Restart=no
    And I stop Hermes gateway systemd service
    And I stop Docker containers (sdc-neo4j, sdc-qdrant, sdc-redis)
    Then laptop load drops from 9.24 to 2.95
    And no duplicate services remain running

  Scenario: Sync skills and unify configs
    Given VPS has 0 OpenClaw skills
    When I rsync 42 skills from laptop to VPS
    And I simplify SDC config from 278 to 193 lines
    And I create tui.json
    Then VPS has all 42 skills available
    And global config has shared agents + MCP + permissions
