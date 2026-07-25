Feature: Agent Galaxy — Public Agent Marketplace
  As a potential customer of Aztro Tech
  I want to explore AI agents as an interactive 3D galaxy
  So that I can understand capabilities and onboard instantly via my phone

  Background:
    Given the Agent Galaxy application is running
    And the galaxy data contains 9 celestial bodies: Mercurio, Venus, Tauro, Marte, Júpiter, Saturno, Urano, Neptuno, Plutón
    And each celestial body has associated capabilities and benefits

  Scenario: User sees the galaxy and zooms in to explore an agent
    Given I open the Agent Galaxy page in a modern browser
    When the page loads completely
    Then I see a 3D galaxy with orbiting celestial bodies
    And the galaxy renders at ≥30fps
    When I zoom in on the "Marte" celestial body
    Then floating cards appear showing agent capabilities
    And each card has animated text with fade-in/fade-out effects
    And I can read the agent's benefits and specifications

  Scenario: User onboards via QR code scan
    Given I am viewing the Agent Galaxy page
    And I am interested in the "Júpiter" agent
    When I click the onboarding button for "Júpiter"
    Then a QR code is generated on screen
    And a direct link is also available
    When I scan the QR with my phone
    And I complete the onboarding form on my phone
    Then a new tenant is created in the system
    And capabilities are assigned based on my needs
    And the onboarding_completed event is emitted
    And I receive my agent configuration via WhatsApp

  Scenario: Multi-tenant — two different users see different agent configurations
    Given tenant "user-alpha" exists with plan "conquistador"
    And tenant "user-beta" exists with plan "explorador"
    When tenant "user-alpha" accesses their agent dashboard
    Then they see full capabilities: voice STT/TTS, multi-social-network, OpenClaw integration, all skills
    When tenant "user-beta" accesses their agent dashboard
    Then they see limited capabilities: text-only, single network, basic skills
    And user-alpha cannot see user-beta's configuration
    And user-beta cannot see user-alpha's configuration

  Scenario: Edge case — browser without WebGL support
    Given I open the Agent Galaxy page in a browser without WebGL
    When the page attempts to render the 3D galaxy
    Then a fallback 2D static view is displayed
    And an informative message explains the browser limitation
    And all onboarding functionality remains available

  Scenario: Edge case — network failure during 3D asset loading
    Given I am on the Agent Galaxy page with a slow connection
    When the 3D assets begin loading
    Then a skeleton screen is displayed
    And assets load progressively as they become available
    And if loading fails after 30 seconds
    Then the fallback 2D view is activated automatically

  Scenario: Edge case — WhatsApp not available for voice pipeline
    Given a tenant has requested voice STT/TTS configuration
    And wacli is not available or WhatsApp API is not configured
    When the voice pipeline setup is attempted
    Then the system degrades gracefully to text-only mode
    And the user is informed of the limitation
    And the voice_pipeline_error event is emitted with degradation details
    And alternative setup instructions are provided (Telegram, web)

  Scenario: Edge case — onboarding interrupted mid-flow
    Given I started the onboarding process
    And I received a unique session link
    When I close my browser before completing onboarding
    And I reopen the unique session link later
    Then my onboarding session is recovered
    And I can continue from where I left off

  Scenario: Voice pipeline end-to-end via WhatsApp
    Given a tenant has voice STT/TTS configured via WhatsApp
    When I send a voice message via WhatsApp
    Then the message is received by wacli
    And STT converts the audio to text
    And the agent processes the text
    And TTS generates an audio response
    And the audio response is sent back via WhatsApp
    And both voice_message_received and voice_message_processed events are emitted
