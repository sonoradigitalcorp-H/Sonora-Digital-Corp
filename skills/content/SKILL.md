# skills/content — Daily Content Factory Pipeline

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-CNT-001

---

## 1. Business Objective

Operate an unattended daily content factory that generates videos, reels, and podcasts for all tenants, transforming raw artist data into published multi-format assets.

## 2. Inputs (Gherkin)

```gherkin
Given tenant content configuration exists (artists, templates, schedules)
And the daily pipeline trigger fires at 06:00 UTC
When RAG context is available (stats, news, trends for each artist)
```

## 3. Outputs (Gherkin)

```gherkin
Then each artist gets generated video, transcript, and subtitles
And all assets are uploaded to tenant storage
And a pipeline summary report is saved to Engram
```

## 4. Events

```
Events:
- content:video:generated: a video asset was created and stored
- content:pipeline:started: the daily content pipeline began
- content:pipeline:completed: the pipeline finished for all tenants
- content:pipeline:partial: pipeline finished but some artists failed
```

## 5. Dependencies

```
Dependencies:
- RAG index: data — artist context, stats, and trends
- LLM provider: service — script generation
- FAL AI: service — video generation
- Whisper: service — transcription and subtitle generation
- Engram: service — pipeline recording and history
```

## 6. Tools

```
Tools:
- generate_video: create video from script via FAL AI
- tts_generate: generate voiceover audio
- whisper_transcribe: create subtitles and transcripts
- upload_file: store assets to tenant storage
- engram_save: record pipeline results
```

## 7. Policies

```
Policies:
- Pipeline must complete within 60 minutes
- All generated content must be watermarked with tenant ID
- Artists without sufficient context must be skipped (not blocked)
- Failed generations must be retried once before marking as failed
- Content must pass NSFW moderation before publishing
```

## 8. Success Metrics

```gherkin
Success Metrics:
- pipeline_duration: Given pipeline start When completed Then total time
  Target: < 45 min
- generation_rate: Given artists configured When generated Then success rate per artist
  Target: > 95%
- publish_time: Given raw video When published Then time to multi-format distribution
  Target: < 10 min
```

## 9. Failure Conditions

```
Failure Conditions:
- Model timeout: FAL generation exceeds 120s (detect via API timeout)
- Transcription failure: Whisper returns empty result (detect via output length)
- Storage full: upload target has insufficient space (detect via HTTP 507)
- Context missing: RAG returns empty for artist (detect via result set size)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. Retry failed generation once with same parameters
2. If second attempt fails → skip artist, log detailed error
3. If storage fails → attempt alternate storage path
4. If transcription fails → proceed without subtitles, flag for manual review
5. Log all results to state/logs/skills/content.log
6. Send daily summary to Dev OS channel
```

## 11. Business Value

```
Business Value: Daily content factory runs unattended. Estimated 15h/week saved.
```

## 12. Parent OS

```
Parent OS: Dev
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-CNT-001
- Events: content:video:generated, content:pipeline:started, content:pipeline:completed, content:pipeline:partial
- Logs: state/logs/skills/content.log
```
