Feature: Content Pipeline
  As a content agent
  I want to generate daily videos for ABE Music artists
  So that each artist gets fresh content every day

  Scenario: Full daily pipeline runs for all active artists
    Given the system has 3 active artists: Hector Rubio, Jesus Urquijo, Javier Arvayo
    When the daily content pipeline triggers at 6:00 AM
    Then each artist gets a script generated with their stats
    And each script passes Promptfoo eval with score ≥85
    And a video is generated via FAL with the artist's LoRA
    And the video is exported in 4 platform formats
    And the results are saved in Engram
    And a notification is sent via Telegram
    And the total pipeline duration is less than 300 seconds

  Scenario: Pipeline handles artist with no stats
    Given an artist has 0 streams and $0 revenue
    When the pipeline runs for this artist
    Then the script still generates without stats context
    And the video is still created
    And the Engram record notes "no_stats"

  Scenario: Pipeline handles FAL API failure
    Given the FAL API returns a 500 error
    When generate_video is called
    Then the pipeline retries up to 2 times
    And after 3 failures it publishes "agent:content:failed"
    And the failure is recorded in Engram
    And other artists are still processed normally

  Scenario: Pipeline B (FLUX + FFmpeg) when FAL video unavailable
    Given FAL video API is not available
    When generate_video runs in Pipeline B mode
    Then it generates images via FLUX + LoRA
    And it creates a slideshow with FFmpeg ken burns
    And it adds TTS voiceover
    And the output is a valid video file with audio

  Scenario: Pipeline prevents duplicate runs
    Given the daily content pipeline is already running
    When a second trigger fires
    Then the second run is rejected
    And a warning is logged

  Scenario: Pipeline recovers from partial failure
    Given artist 1 succeeds and artist 2 fails
    When the pipeline runs
    Then artist 1 content is saved normally
    And artist 2 error is recorded in Engram
    And artist 3 still processes
    And the final notification mentions the partial failure
