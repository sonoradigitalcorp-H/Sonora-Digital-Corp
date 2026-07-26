Feature: Twilio Voice Bridge
  As a partner (e.g., César)
  I want Mystic to make and receive phone calls with my clients
  So that I can provide 24/7 voice support without hiring staff

  Scenario: Receive incoming call
    Given a client calls the partner's Twilio number
    When Twilio triggers the /twilio/incoming webhook
    Then Mystic answers with Kokoro TTS greeting
    And the call is recorded in cost_tracker
    And the transcript is saved to Engram

  Scenario: Make outbound call to lead
    Given the partner sends POST /twilio/call/outbound with lead phone
    When Twilio connects the call
    Then Mystic speaks the sales pitch with Kokoro TTS
    And the lead's responses are transcribed with Whisper STT
    And the call result is saved to Engram

  Scenario: Call costs less than $0.20 for 10 minutes
    Given a Twilio call lasts 10 minutes
    When the call ends
    Then total cost < $0.20 ($0.15 Twilio + $0.001 deepseek)
    And the cost is logged in cost_tracker

  Scenario: Audio format conversion
    Given Kokoro outputs 24kHz WAV
    When the audio is sent to Twilio
    Then it is converted to 8kHz PCMU
    And the partner hears clear natural speech

Feature: Tokenomics — Partner Pricing
  As a partner
  I want to set my own prices for each action
  So that I can maximize my margin

  Scenario: Partner sets call price
    Given the partner configures call price at $3.00
    When a call is made
    Then the client is charged $3.00
    And SDC deducts its cost ($0.15)
    And the partner sees their revenue ($2.85)
    And the partner does NOT see SDC's cost

  Scenario: SDC commission is hidden
    Given the partner views their dashboard
    When they check their earnings
    Then they see "Total earned: $2,850.00"
    And they do NOT see "SDC cost: $150.00"
    And they do NOT see "SDC commission: 5%"

  Scenario: Volume discount
    Given a partner has 10+ active clients
    When they reach 100,000 interactions/month
    Then their commission rate drops from 30% to 20%
    And the dashboard shows their improved rate

Feature: Gamification
  As an end user
  I want to earn rewards for using and improving my agent
  So that I stay engaged and motivated

  Scenario: User earns XP for training
    Given the user corrects an agent response
    When the correction is saved
    Then the user gains 10 XP
    And their progress bar updates

  Scenario: User levels up
    Given the user has 1000 XP
    When they reach the threshold
    Then they advance to Level 2
    And they unlock a new capability
    And a celebration notification is shown

  Scenario: Daily challenge
    Given it's a new day
    When the user opens their agent
    Then a daily challenge is presented ("Complete 5 conversations")
    And completing it awards 50 bonus XP

  Scenario: Referral commission
    Given Partner A refers Client B to the platform
    When Client B makes their first payment
    Then Partner A receives 10% of Client B's first month
    And the commission is logged in cost_tracker
    And Partner A sees the referral in their dashboard

Feature: Conscious Agent
  As an end user
  I want my agent to remember me and adapt to my style
  So that interactions feel personal and natural

  Scenario: Agent remembers user across sessions
    Given the user calls on Monday and says "I have a meeting at 3pm"
    When the user calls again on Wednesday
    Then the agent says "Welcome back! How did the meeting go?"
    And the user feels recognized

  Scenario: Agent adapts to user tone
    Given the user speaks rapidly and with high energy
    When the agent detects this pattern
    Then the agent matches with energetic, concise responses
    And the user feels understood

  Scenario: Agent detects emotion
    Given the user sounds frustrated
    When Whisper STT + tone analysis detects anger
    Then the agent responds with calming, empathetic language
    And escalates to human if needed
