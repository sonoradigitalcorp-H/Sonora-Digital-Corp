Feature: Sonora OS Foundation
  As a platform architect
  I want the Hasura + Supabase + Telegram + LangChain stack operational
  So that multi-tenant clients can interact via bot, earn $BEAT, and see live dashboards

  Background:
    Given Docker services are running
    And Supabase project exists with valid credentials
    And Hasura is connected to the PostgreSQL database
    And the Telegram bot token is configured

  # ─── FR1: Auth ───

  @happy @fr1
  Scenario: User signs up with Google OAuth
    Given a new user visits the platform
    When they click "Sign in with Google"
    Then Supabase Auth creates a new user record
    And a JWT token is returned with role "client_admin"

  @edge @fr1
  Scenario: User signs up with invalid email domain
    Given a user with email "test@spam.com" tries to register
    When the auth system validates the domain
    Then access is denied with "domain_not_allowed"
    And no user record is created

  # ─── FR2: Hasura GraphQL ───

  @happy @fr2
  Scenario: Hasura exposes auto-generated GraphQL schema
    Given PostgreSQL has the "artists" table with columns id, name, tenant_id
    When I query the Hasura GraphQL endpoint
    Then the response contains "artists" with proper types

  @happy @fr2
  Scenario: Hasura JWT auth rejects unauthenticated requests
    Given I have a valid Supabase JWT for tenant "abe-music"
    When I query artists with X-Hasura-Role: client_admin
    Then I only see artists where tenant_id matches my JWT claim

  @error @fr2
  Scenario: Hasura rejects expired JWT
    Given my JWT token is expired
    When I make a GraphQL request
    Then Hasura returns 401 "invalid-jwt"

  # ─── FR3: Schema ───

  @happy @fr3
  Scenario: All required tables exist in PostgreSQL
    Given Hasura is tracking the public schema
    When I list all tracked tables
    Then the following tables exist:
      | tenants         |
      | users           |
      | telegram_users  |
      | token_ledger    |
      | greetings       |
      | transactions    |
      | quests          |
      | quest_completions |
      | rewards         |
      | schedules       |
      | auto_messages   |
      | notifications   |
      | content_generations |
      | knowledge_bases |
      | scraped_metrics |

  @happy @fr3
  Scenario: Tenant isolation via RLS
    Given tenant "abe-music" has 3 artists
    And tenant "mystik" has 2 artists
    When user from "abe-music" queries the artists table
    Then they only see the 3 artists from "abe-music"
    And cannot see the 2 artists from "mystik"

  # ─── FR4: Telegram Bot ───

  @happy @fr4
  Scenario: Bot receives message and routes to Redis
    Given the Telegram bot is running and connected
    When a user sends "Hola" to the bot
    Then the bot receives the update
    And the message is pushed to Redis queue "telegram:inbox"
    And no business logic runs in the bot process itself

  @happy @fr4
  Scenario: Bot delivers response from Redis
    Given Redis queue "telegram:outbox" has a pending message for chat_id 12345
    When the bot consumer processes the queue
    Then the message is sent to chat_id 12345 via Telegram API
    And the queue item is marked as delivered

  @edge @fr4
  Scenario: Bot receives non-text message (photo, sticker)
    Given a user sends a photo to the bot
    When the bot receives the update
    Then the message type is detected as "photo"
    And a "photo_received" event is pushed to Redis
    And the user receives a response: "Solo proceso mensajes de texto por ahora"

  # ─── FR5: LangChain Router ───

  @happy @fr5
  Scenario: Router detects tenant from user
    Given Redis queue "telegram:inbox" has a message from telegram_id 67890
    And telegram_users table maps 67890 to tenant "abe-music"
    When the LangChain Router Agent processes the message
    Then it loads tenant config for "abe-music"
    And routes to the appropriate sub-agent

  @happy @fr5
  Scenario: Chat Agent responds with RAG context
    Given a user asks "Cuanto streams tiene Hector Rubio"
    When the Chat Agent queries the RAG for tenant "abe-music"
    Then it returns a response with actual stream count from PostgreSQL
    And includes sources from Open Notebook

  @happy @fr5
  Scenario: Monetization Agent processes a greeting request
    Given a user says "Quiero un saludo de cumpleanos de Javier"
    When the Monetization Agent processes the request
    Then it returns a payment link (Stripe) or $BEAT cost
    And creates a pending greeting record

  # ─── FR6: Playwright Scraping ───

  @happy @fr6
  Scenario: Daily scraping extracts artist metrics
    Given it is 6:00 AM
    When the Playwright cron job runs
    Then it navigates to Spotify artist page for each artist
    And extracts: monthly listeners, followers, top songs
    And stores results in the scraped_metrics table
    And emits event "scraping:completed"

  @error @fr6
  Scenario: Scraping fails gracefully
    Given the Spotify page is unreachable
    When the Playwright script attempts to navigate
    Then it retries 3 times with 30s delay
    And if all retries fail, it logs the error
    And emits event "scraping:failed"
    And does not crash the pipeline

  # ─── FR7: RAG por Cliente ───

  @happy @fr7
  Scenario: Client has dedicated RAG collection
    Given a new client "artist-x" is onboarded
    When the onboarding process completes
    Then a new Qdrant collection "artist-x" is created
    And a new Open Notebook project "artist-x" is initialized
    And documents uploaded by "artist-x" are only searchable by their tenant

  @happy @fr7
  Scenario: RAG query returns tenant-specific results
    Given tenant "abe-music" has 50 documents indexed
    And tenant "other" has 20 documents indexed
    When a user from "abe-music" queries the RAG
    Then results only include documents from "abe-music"
    And no documents from "other" leak into results

  # ─── FR8: WebSocket Streaming ───

  @happy @fr8
  Scenario: Dashboard receives agent events in real-time
    Given a client dashboard has an open WebSocket connection
    When a LangChain agent completes a task
    Then an event is pushed to Redis "agent:events"
    And the WebSocket server forwards it to the dashboard
    And the dashboard updates within 500ms

  @happy @fr8
  Scenario: Multiple clients receive isolated events
    Given client A and client B both have open WebSockets
    When an event for client A is emitted
    Then client A receives the event
    And client B does NOT receive the event

  # ─── FR9: Multi-tenant Isolation ───

  @happy @fr9
  Scenario: Admin can see all tenants
    Given I authenticate with role "platform_admin"
    When I query the tenants table via Hasura
    Then I see all tenants in the system

  @happy @fr9
  Scenario: Client admin only sees own tenant
    Given I authenticate with role "client_admin" for tenant "abe-music"
    When I query any table with tenant_id
    Then Hasura automatically filters by my tenant_id
    And I cannot access data from other tenants

  @error @fr9
  Scenario: Cross-tenant data access is blocked
    Given I have a valid JWT for tenant "abe-music"
    When I attempt to set X-Hasura-Tenant-Id to "other-tenant" in my headers
    Then Hasura rejects the request due to session variable conflict
    And returns "cannot set session variable that conflicts with JWT claim"

  # ─── FR10: Tests Verdes ───

  @happy @fr10
  Scenario: All tests pass before deployment
    Given the codebase has been modified
    When I run pytest with coverage
    Then all tests pass with status "PASSED"
    And coverage is >= 70 for new modules
    And lint reports 0 errors
