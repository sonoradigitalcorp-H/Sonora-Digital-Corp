# Generate Video — Business Capability Spec

**Version**: 1.0.0 | **Status**: experimental | **Owner**: video-agent
**Business Domain**: music | **Cost Tier**: 4

## Description

Generate talking head or lipsync videos from audio + image, using ComfyUI + DreamShaper.

## Invariants

| ID | Rule | Critical |
|----|------|----------|
| INV-001 | All generated videos MUST include watermark | yes |
| INV-002 | Generation time MUST not exceed 5 min per clip | yes |
| INV-003 | Source image MUST be minimum 512x512 | yes |

## Inputs

- Source image (face, high quality)
- Audio track (speech or singing, up to 60s)
- Style reference (optional)

## Outputs

- MP4 video file (lipsync talking head)
- Thumbnail preview

## Events

| Event | Description | Produces |
|-------|-------------|----------|
| video.generation.started | Pipeline initiated | job_id, params |
| video.generation.completed | Video ready | job_id, video_uri |
| video.generation.failed | Pipeline error | job_id, error |

## Success Criteria

| ID | Criterion | Measurable |
|----|-----------|------------|
| SC-001 | Lipsync accuracy > 90% frame match | yes |
| SC-002 | Generation under 5 min on CPU | yes |
| SC-003 | Watermark visible and non-removable | yes |

## Dependencies

| Capability | Type |
|------------|------|
| clone-person | soft |

## Security Classification

internal

## LLM Fit

| Dimension | Value |
|-----------|-------|
| Complexity | high |
| Reasoning Level | medium |
| Domain Specialization | domain |
