Feature: Sonora OS Gamification + Monetization + Dashboard
  As a platform architect
  I want quests, payments, and live dashboards operational
  So that fans earn $BEAT, pay for greetings, and clients see metrics in real-time

  Background:
    Given Sonora OS foundation is deployed
    And user is registered and logged in

  # ─── FR1: Quests ───

  @happy @fr1
  Scenario: Fan completes a Play quest (daily trivia)
    Given fan answers the daily trivia correctly
    When the quest engine validates completion
    Then 3 $BEAT are awarded
    And quest_completions records the completion
    And event "gamification:quest:completed" is emitted

  @happy @fr1
  Scenario: Fan completes a Work quest (referral)
    Given fan shares artist link with 3 friends
    When the quest engine validates 3 referrals
    Then 15 $BEAT are awarded
    And the fan's referral count increases

  @happy @fr1
  Scenario: Fan completes a Learn quest (watch video)
    Given fan watches the full "behind the scenes" video
    When the quest engine detects 100% progress
    Then 10 $BEAT are awarded
    And event "gamification:quest:completed" is emitted

  @edge @fr1
  Scenario: Fan tries to complete same quest twice
    Given fan already completed the daily trivia today
    When they try to answer again
    Then the quest engine returns "already_completed"
    And no $BEAT are awarded

  # ─── FR2: Levels ───

  @happy @fr2
  Scenario: Fan levels up from Bronze to Silver
    Given fan has 90 XP (Bronze, threshold=100 for Silver)
    When they earn 15 XP from a quest
    Then their total XP is 105
    And their level changes to "silver"
    And event "gamification:levelup" is emitted
    And they unlock Silver benefits

  @happy @fr2
  Scenario: Fan reaches Platinum tier
    Given fan has 950 XP (Gold, threshold=1000 for Platinum)
    When they earn 50 XP from multiple quests
    Then their level changes to "platinum"
    And they unlock exclusive content access

  # ─── FR3: Rewards ───

  @happy @fr3
  Scenario: $BEAT reward is deducted from client pool
    Given client "abe-music" has pool of 1,000,000 $BEAT
    When 100 $BEAT are rewarded to fans
    Then the pool decreases to 999,900
    And token_ledger records the earn transactions

  @error @fr3
  Scenario: Pool exhausted prevents rewards
    Given client pool has 3 $BEAT remaining
    When a quest would award 5 $BEAT
    Then the reward is not issued
    And event "gamification:pool:exhausted" is emitted
    And the admin is notified

  # ─── FR4: Stripe Checkout ───

  @happy @fr4
  Scenario: Fan pays for greeting via Stripe
    Given fan wants a personalized greeting for $5 USD
    When they click "Pay with Card"
    Then a Stripe Checkout Session is created
    And the fan is redirected to Stripe
    And a pending transaction record is created

  @happy @fr4
  Scenario: Stripe webhook confirms payment
    Given Stripe sends checkout.session.completed event
    When the webhook handler processes it
    Then the transaction status changes to "completed"
    And the greeting status changes to "paid"
    And event "payment:stripe:completed" is emitted

  # ─── FR5: $BEAT Ledger ───

  @happy @fr5
  Scenario: Fan burns $BEAT for greeting
    Given fan has 200 $BEAT balance
    When they spend 50 $BEAT on a greeting
    Then their balance decreases to 150
    And 25 $BEAT are burned (50% burn)
    And 25 $BEAT go to the artist
    And token_ledger records: -50 fan, +25 artist, -25 burn

  @happy @fr5
  Scenario: Fan transfers $BEAT to another user
    Given fan A has 100 $BEAT and fan B has 50 $BEAT
    When fan A transfers 30 $BEAT to fan B
    Then fan A has 70 $BEAT
    And fan B has 80 $BEAT

  @error @fr5
  Scenario: Insufficient $BEAT for transaction
    Given fan has 20 $BEAT
    When they try to spend 50 $BEAT on a greeting
    Then the transaction is rejected
    And they are offered a fiat payment alternative

  # ─── FR6: Hybrid Greeting ───

  @happy @fr6
  Scenario: AI generates greeting for artist approval
    Given a greeting has been paid (status=paid)
    When the AI generates audio via OmniVoice
    Then the audio URL is saved
    And the greeting status changes to "pending_approval"
    And the artist is notified via Telegram

  @happy @fr6
  Scenario: Artist approves greeting
    Given a greeting is pending_approval
    When the artist approves it
    Then the greeting status changes to "approved"
    And the audio is delivered to the fan
    And event "greeting:approved" is emitted

  @edge @fr6
  Scenario: Artist rejects greeting
    Given a greeting is pending_approval
    When the artist rejects it
    Then the greeting status changes to "rejected"
    And the fan receives a refund ($BEAT or fiat)
    And event "greeting:rejected" is emitted

  # ─── FR7: Dashboard REST ───

  @happy @fr7
  Scenario: Dashboard returns revenue stats
    Given the client dashboard is loaded
    When I GET /api/v1/dashboard/revenue
    Then the response contains total_revenue, monthly_revenue, daily_breakdown
    And the data is scoped to the requesting tenant

  @happy @fr7
  Scenario: Dashboard returns token circulation
    Given the client has token activity
    When I GET /api/v1/dashboard/tokens
    Then the response contains total_supply, circulating, burned, earned_today

  @happy @fr7
  Scenario: Dashboard returns greeting stats
    Given the client has greeting activity
    When I GET /api/v1/dashboard/greetings
    Then the response contains total, pending, approved, rejected counts

  # ─── FR8: WebSocket Events ───

  @happy @fr8
  Scenario: Dashboard receives live quest completion
    Given a dashboard WebSocket is connected
    When a fan completes a quest
    Then the WebSocket receives event "gamification:quest:completed"
    And the payload includes fan_id, quest_id, reward

  @happy @fr8
  Scenario: Dashboard receives live payment
    Given a dashboard WebSocket is connected
    When a Stripe payment completes
    Then the WebSocket receives event "payment:stripe:completed"
    And the payload includes amount, greeting_id

  # ─── FR9: Leaderboard ───

  @happy @fr9
  Scenario: Leaderboard shows top fans by XP
    Given there are 10 fans with XP scores
    When I GET /api/v1/dashboard/leaderboard
    Then the top 5 fans are returned ordered by XP descending
    And each entry shows rank, name, XP, level, $BEAT balance

  @happy @fr9
  Scenario: Leaderboard updates after quest
    Given the leaderboard shows fan A at #1 with 500 XP
    When fan B completes a quest worth 100 XP (from 450 to 550)
    Then the leaderboard recalculates
    And fan B moves to #1

  # ─── FR10: Tests Green ───

  @happy @fr10
  Scenario: All new tests pass
    Given the codebase has been modified
    When I run pytest for gamification, payments, and dashboard tests
    Then all tests pass with status "PASSED"
