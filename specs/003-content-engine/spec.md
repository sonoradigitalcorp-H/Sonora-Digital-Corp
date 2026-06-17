# Feature Specification: Content Engine & Automation

**Feature Branch**: `003-content-engine`

**Created**: 2026-06-10

**Status**: Draft

**Input**: Automated content pipeline with n8n workflows, video generation, social media automation, content scheduling, and Agent CFO for business intelligence.

## User Scenarios & Testing

### User Story 1 - n8n workflow automation (Priority: P1)

The user configures automated workflows via n8n: content creation triggers, social posting schedules, notification chains, and integration bridges between services.

**Why this priority**: n8n is the automation backbone. Without workflows, every task is manual.

**Independent Test**: Create a test workflow that posts to a webhook on a timer, verify execution in n8n history.

**Acceptance Scenarios**:

1. **Given** a configured n8n workflow, **When** the trigger fires (timer, webhook, event), **Then** the workflow executes all nodes successfully.
2. **Given** a workflow with a failure, **When** an error node triggers, **Then** it retries with configurable backoff and logs the error.
3. **Given** a workflow that calls an external API, **When** the API is down, **Then** the workflow retries up to N times then notifies the admin.
4. **Given** n8n is deployed via Docker, **When** the container restarts, **Then** all workflows resume from saved state.

---

### User Story 2 - Content pipeline: generate, approve, publish (Priority: P1)

The user triggers content generation (text, images, audio), reviews in a dashboard, approves, and schedules publishing across platforms.

**Why this priority**: Content is the product. Without generation + publishing, there is no value.

**Independent Test**: Generate a blog post via the pipeline, approve it in the dashboard, schedule it, verify it publishes at the scheduled time.

**Acceptance Scenarios**:

1. **Given** a content brief, **When** the pipeline runs, **Then** it generates a draft with text, image, and metadata.
2. **Given** a generated draft, **When** the user views it in the dashboard, **Then** they can edit, approve, reject, or request regeneration.
3. **Given** an approved piece, **When** scheduled, **Then** it publishes to the configured platforms at the exact scheduled time.
4. **Given** a content failure (model down, API error), **When** generation fails, **Then** the pipeline reports the error and retries.

---

### User Story 3 - Video pipeline: script → voice → render (Priority: P2)

The user creates short-form videos (TikTok/Reels/Shorts) from a script: text-to-speech voiceover, stock footage assembly, subtitle overlay, and platform-optimized export.

**Why this priority**: Short-form video is the highest-ROI content format. Depends on US2.

**Independent Test**: Submit a 60-word script, verify the pipeline produces a rendered MP4 with voiceover and subtitles.

**Acceptance Scenarios**:

1. **Given** a script of 30-300 words, **When** submitted to the video pipeline, **Then** it generates a video with AI voiceover, background footage, and subtitles.
2. **Given** a generated video, **When** previewed, **Then** the user can adjust voice, style, and footage before final render.
3. **Given** a final render, **When** approved, **Then** it auto-publishes to connected social platforms at the scheduled time.
4. **Given** insufficient footage for the script length, **When** the pipeline detects it, **Then** it loops or extends existing clips with crossfade.

---

### User Story 4 - Social media automation (Priority: P2)

Content is automatically posted to connected social platforms (Instagram, TikTok, YouTube, Twitter/X, LinkedIn) on schedule, with platform-specific formatting.

**Why this priority**: Multi-platform distribution multiplies reach. Depends on US2 and US3.

**Independent Test**: Schedule a post, verify it appears on all connected social platforms at the correct time.

**Acceptance Scenarios**:

1. **Given** a content piece ready for distribution, **When** the schedule triggers, **Then** it posts to all configured platforms with correct formatting.
2. **Given** a platform API error, **When** posting fails, **Then** the system retries up to 3 times then logs the failure.
3. **Given** platform-specific formatting requirements, **When** posting, **Then** each post is adapted (hashtag count, image ratio, video length, character limit).
4. **Given** a post that violates platform guidelines, **When** detected, **Then** it is rejected with explanation before posting.

---

### User Story 5 - Agent CFO: business intelligence (Priority: P3)

The user accesses an automated CFO dashboard that tracks revenue, costs, content performance, growth metrics, and provides recommendations.

**Why this priority**: Strategic decision support. Depends on US2 (content metrics) and payments from 002-sdc-business.

**Independent Test**: Generate content for a week, verify the CFO dashboard shows revenue, content performance, and growth trends.

**Acceptance Scenarios**:

1. **Given** business data (revenue, content, users), **When** the CFO dashboard loads, **Then** it shows revenue trends, content performance, and growth metrics.
2. **Given** a revenue decline, **When** detected, **Then** Agent CFO highlights the trend and suggests corrective actions.
3. **Given** content performance data, **When** analyzed, **Then** Agent CFO recommends optimal posting times, formats, and topics.

---

### Edge Cases

- **n8n workflow infinite loop**: max execution depth guard
- **Content generation toxic/NSFW output**: filter before dashboard
- **Video pipeline TTS language mismatch**: detect and warn before render
- **Social platform rate limits**: queue and stagger posts
- **Agent CFO no data yet**: show onboarding state, not zero/error
- **Scheduled post at nonexistent time (DST change)**: clamp to valid time, log adjustment

## Requirements

### Functional Requirements

**n8n workflows**

- **FR-001**: The system MUST run n8n in Docker with persistent workflow storage.
- **FR-002**: Workflows MUST support triggers: timer, webhook, event, and manual.
- **FR-003**: Failed workflow nodes MUST retry with configurable backoff.

**Content pipeline**

- **FR-004**: The pipeline MUST generate text content from a brief using available LLM.
- **FR-005**: The pipeline MUST generate accompanying images (via ComfyUI or API).
- **FR-006**: A review dashboard MUST allow edit, approve, reject, and regenerate.

**Video pipeline**

- **FR-007**: The pipeline MUST convert a script (30-300 words) into a video with TTS, footage, and subtitles.
- **FR-008**: The pipeline MUST support multiple voice styles and languages.
- **FR-009**: Output MUST be MP4 with platform-optimized aspect ratios (9:16, 16:9, 1:1).

**Social automation**

- **FR-010**: The system MUST support posting to Instagram, TikTok, YouTube, X/Twitter, and LinkedIn.
- **FR-011**: Posts MUST be scheduleable with platform-specific formatting.
- **FR-012**: Failed posts MUST retry up to 3 times with error logging.

**Agent CFO**

- **FR-013**: The dashboard MUST show revenue, costs, content performance, and growth trends.
- **FR-014**: Agent CFO MUST detect trends and suggest actions based on data.
- **FR-015**: Recommendations MUST be explainable and traceable to source data.

**General**

- **FR-016**: All content MUST pass safety filters before publishing.
- **FR-017**: Platform credentials MUST be stored encrypted.

### Key Entities

- **Workflow**: n8n DAG with trigger, nodes, and error handling
- **Content**: draft with text, image, metadata, status (draft/approved/rejected/published)
- **Video**: script, voiceover, footage, subtitles, rendered MP4
- **Schedule**: content + platform + timestamp with status
- **Metric**: revenue, cost, performance, growth data point

## Success Criteria

### Measurable Outcomes

- **SC-001**: n8n workflow execution success rate >= 95%.
- **SC-002**: Content pipeline generates draft in < 60s (text + image).
- **SC-003**: Video pipeline renders a 60s video in < 5 minutes.
- **SC-004**: Social posts publish within 1 minute of scheduled time in >= 99% of cases.
- **SC-005**: Agent CFO dashboard renders in < 3s with data.
- **SC-006**: Zero content published that violates safety filters.

## Assumptions

- **n8n self-hosted**: via Docker on local/private cloud; not n8n cloud
- **Video rendering**: local GPU available (NVIDIA) for ComfyUI/FFmpeg; CPU fallback is slower but supported
- **TTS**: ElevenLabs API or local model; assumes API key or local model available
- **Social APIs**: platform APIs may change rate limits; monitoring and alerting needed
- **CFO data source**: reads from SDC business DB (spec 002); no separate data pipeline
- **Content volume**: < 100 pieces/day; beyond needs horizontal scaling
