# Internal Module Contracts: Content Engine & Automation

**Feature**: `003-content-engine`

## `ContentGenerator`

```python
def generate_text(brief: str, style: str, length: int) -> ContentDraft
def generate_image(prompt: str, style: str, size: tuple) -> ImageAsset
def generate_draft(brief: dict) -> ContentDraft  # text + image + metadata
```

- LLM for text generation (via external API, mockable)
- ComfyUI or fal.ai for image generation
- Returns `ContentDraft` with text, image URL, metadata

## `VideoPipeline`

```python
def render_short(script: str, voice: str, duration: int) -> VideoAsset
def select_footage(script: str, style: str) -> list[Clip]
def generate_subtitles(audio_path: str) -> SRT
def export_mp4(clips: list[Clip], audio: str, subtitles: SRT, ratio: str) -> VideoAsset
```

- Script 30-300 words → MP4 output
- TTS via ElevenLabs or local model
- Footage from stock library or AI-generated
- Ratios: 9:16 (vertical), 16:9 (horizontal), 1:1 (square)

## `SocialPublisher`

```python
def post_to_platform(content: Content, platform: str) -> PostResult
def schedule_post(content: Content, platform: str, timestamp: datetime) -> ScheduleEntry
def check_platform_limits(platform: str) -> RateLimit
def format_for_platform(content: Content, platform: str) -> FormattedPost
```

- Each platform has independent adapter (Instagram, TikTok, YouTube, X, LinkedIn)
- Platform-specific formatting: hashtag count, image ratio, video length, char limit
- Failed posts retry up to 3 times then log

## `SafetyFilter`

```python
def check_content(text: str, image: ImageAsset | None) -> SafetyVerdict
def check_video(video: VideoAsset) -> SafetyVerdict
```

- Returns PASS/FLAG/BLOCK with explanation
- Must be called before any content enters review dashboard
- Blocked content is quarantined, not deleted
