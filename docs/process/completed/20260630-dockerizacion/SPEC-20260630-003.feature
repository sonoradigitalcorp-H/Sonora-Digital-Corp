Feature: Docker Migration
  As a system engineer
  I want Jarvis Core and WebUI to run in Docker containers
  So that infrastructure is portable and Python version independent

  Background:
    Given Docker Engine is installed
    And docker-compose.yml exists with data services
    And .env file contains all secrets

  Scenario: Build succeeds
    Given the Dockerfile exists for jarvis
    When I run "docker compose build jarvis"
    Then the build exits with code 0

  Scenario: All containers healthy
    Given docker compose is running
    When I check "docker ps"
    Then all containers show "healthy" or "running"

  Scenario: WebUI responds
    Given the webui container is running
    When I curl localhost:5174/api/enterprise-score
    Then the response contains "total"

  Scenario: Systemd shutdown safe
    Given Docker containers are running and healthy
    When I stop jarvis-webui.service
    Then the WebUI is still accessible via Docker
