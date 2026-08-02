Feature: ABE Music Group Platform
  As the founder of ABE Music Group
  I want a world-class digital platform
  So that I can manage my artists, track real-time data, and present to clients

  Background:
    Given the ABE API is running on port 8111
    And the frontend is deployed on Vercel

  # ====== Auth ======

  Scenario: Admin logs in successfully
    Given I am at the login page
    When I submit email "admin@abe.com" and password "admin123"
    Then I receive a valid JWT token
    And I am redirected to the portal dashboard

  Scenario: Invalid credentials are rejected
    Given I am at the login page
    When I submit email "admin@abe.com" and password "wrongpass"
    Then I receive a 401 error
    And the error message is "Invalid credentials"

  Scenario: Unauthenticated user is blocked from portal
    Given I have no auth token
    When I request GET "/api/portal/dashboard"
    Then I receive a 401 response

  Scenario: Non-admin cannot create services
    Given I am logged in as "demo@abe.com" (role: user)
    When I POST to "/api/admin/services" with valid data
    Then I receive a 403 response

  # ====== Stats ======

  Scenario: Executive dashboard shows live stats
    Given the scrapers have completed their latest run
    When I request GET "/api/stats"
    Then the response contains "artists" (integer >= 1)
    And the response contains "total_streams" (integer >= 0)
    And the response contains "services" (integer >= 1)

  # ====== Services CRUD ======

  Scenario: Admin creates a new service
    Given I am logged in as admin
    When I POST to "/api/admin/services" with:
      | title       | "AI Mastering"                     |
      | description | "Automated AI-powered audio mastering" |
      | icon        | "🎛️"                               |
    Then the response status is 200
    And the response body contains "ok: true"
    And the new service appears in GET "/api/services"

  Scenario: Admin deletes a service
    Given I am logged in as admin
    And a service with id "test-123" exists
    When I DELETE "/api/admin/services/test-123"
    Then the response status is 200
    And the service no longer appears in GET "/api/services"

  # ====== Artists CRUD ======

  Scenario: Admin adds a new artist
    Given I am logged in as admin
    When I POST to "/api/admin/artists" with:
      | name   | "New Artist" |
      | streams | 0            |
    Then the response status is 200
    And the response body contains "ok: true"
    And the new artist appears in GET "/api/artists"

  # ====== Contact ======

  Scenario: Visitor submits contact form
    Given I am on the contact page
    When I submit name "John", email "john@test.com", service "Distribution", message "Hello"
    Then the contact is saved
    And I receive a confirmation with "ok: true"

  Scenario: Contact form rejects missing fields
    Given I am on the contact page
    When I submit with empty name
    Then I receive a validation error

  # ====== Portal Dashboard ======

  Scenario: Portal dashboard shows KPIs for authenticated user
    Given I am logged in as any user
    When I request GET "/api/portal/dashboard"
    Then the response contains "total_streams", "revenue", "campaigns", "engagement"

  # ====== Health ======

  Scenario: Health endpoint returns all service statuses
    When I request GET "/api/health"
    Then the response contains "status: ok"
    And the response contains a "services" object
    And the response contains a "timestamp" with ISO format

  # ====== SSE Real-time ======

  Scenario: SSE endpoint streams events
    When I connect to GET "/api/sse"
    Then I receive a text/event-stream content type
    And I receive at least one "event:" line within 30 seconds

  # ====== Scraper Pipeline ======

  Scenario: Scraper pipeline runs and updates data
    Given the scrapers are configured
    When I trigger the scraper pipeline
    Then the artist data is updated in the API
    And an event "scraper.complete" is emitted

  Scenario: Scraper handles API failure gracefully
    Given the Spotify API is returning 429
    When the Spotify scraper runs
    Then it retries with exponential backoff
    And after max retries, it logs a warning
    And the existing data remains unchanged
