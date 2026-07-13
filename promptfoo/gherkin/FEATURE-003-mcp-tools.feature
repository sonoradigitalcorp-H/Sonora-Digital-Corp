Feature: MCP Tools
  As an agent
  I want to access tools via MCP Gateway
  So that I can execute actions across the system

  Scenario: All 49 tools are accessible via MCP Gateway
    Given the MCP Gateway is running on :8180
    When I query /mcp/tools
    Then I receive 49 tools
    And they are organized in 15 servers

  Scenario: Each tool can be executed
    Given tool "hasura_query" exists
    When I execute it with a valid query
    Then I receive a successful response
    And the response contains "data"

  Scenario: Engram saves and retrieves memory
    Given I call engram_save with tenant, key, and value
    When I call engram_get with the same key
    Then I receive the saved value

  Scenario: Upload stores files in Supabase
    Given I have a base64-encoded file
    When I call upload_file
    Then the file is stored in Supabase
    And I receive a public URL

  Scenario: RAG searches knowledge base
    Given a tenant has indexed documents in Qdrant
    When I call rag_search with a relevant query
    Then I receive matching results with scores

  Scenario: Tool validates required params
    Given tool "whisper_transcribe" requires audio_url
    When I call it without audio_url
    Then I receive an error: "audio_url is required"

  Scenario: Whisper transcribes Spanish audio
    Given an audio file in Spanish
    When I call whisper_transcribe
    Then I receive text in Spanish
    And I receive SRT subtitles with timestamps

  Scenario: FFmpeg exports 4 platform formats
    Given a raw video URL
    When I call ffmpeg_multiformat
    Then I receive URLs for tiktok, reels, shorts, and facebook formats
    And each format has the correct dimensions

  Scenario: LoRA training creates consistent artist style
    Given 10 photos of an artist are provided
    When I call train_lora
    Then I receive a weight_id
    And the weight is stored in Hasura
