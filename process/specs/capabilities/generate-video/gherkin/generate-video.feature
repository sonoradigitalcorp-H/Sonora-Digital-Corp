Feature: Generate Video
  As a music marketer
  I want to generate lipsync videos from audio + image
  So that I can create personalized video content

  Background:
    Given the system has ComfyUI running on port 8188
    And DreamShaper model is loaded

  @P1 @critical
  Scenario: Generate basic lipsync video
    Given a source image of 1024x1024
    And an audio track of 30 seconds
    When I request a lipsync video generation
    Then the system queues a ComfyUI workflow
    And returns a job with status "processing"
    And when the job completes, a video file is available
    And the video contains a visible watermark

  @P2
  Scenario: Generation fails with small image
    Given a source image of 100x100
    And an audio track of 10 seconds
    When I request a lipsync video generation
    Then the system rejects with error "IMAGE_TOO_SMALL"
    And no job is created

  @P2
  Scenario: Multiple generation requests are queued
    Given 3 video generation requests submitted simultaneously
    When all are accepted
    Then each request gets a unique job ID
    And jobs are processed in FIFO order
    And all 3 complete successfully

  @P3
  Scenario: Style reference modifies output
    Given a source image and audio
    And a "cinematic" style reference
    When video is generated
    Then the output has cinematic color grading
    And the watermark is still present
