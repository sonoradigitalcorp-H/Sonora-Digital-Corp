# Clone Person — Business Capability Spec

**Version**: 1.0.0 | **Status**: active | **Owner**: clone-agent
**Business Domain**: marketing | **Cost Tier**: 3

## Description

Train facial LoRA + voice clone from client photos/audio, generate advertising content with their identity.

## Invariants

| ID | Rule | Critical |
|----|------|----------|
| INV-001 | Client MUST sign consent form before any training | yes |
| INV-002 | Generated content MUST include disclosure label | yes |
| INV-003 | Original media MUST be deleted 30 days after project delivery | yes |
| INV-004 | Voice clone MUST use only provided audio samples | yes |

## Inputs

- Client photos (5–20, high-res, varied angles)
- Client audio (30–60s clean speech)
- Brand guidelines / creative brief
- Consent form (signed)

## Outputs

- Trained LoRA model (SD 1.5 / SDXL compatible)
- Voice clone model (CosyVoice / Bark)
- Generated advertising content (video + audio)

## Events

| Event | Description | Produces |
|-------|-------------|----------|
| clone.order.created | New clone order placed | order_id, client_id |
| clone.training.started | Training pipeline initiated | order_id, model_type |
| clone.training.completed | LoRA + voice models ready | order_id, model_uris |
| clone.content.generated | Ad content produced | order_id, content_uris |
| clone.delivery.completed | Final delivery sent to client | order_id, delivery_uri |

## Success Criteria

| ID | Criterion | Measurable |
|----|-----------|------------|
| SC-001 | LoRA produces recognizable face in 5/5 test prompts | yes |
| SC-002 | Voice clone preserves tone, pace, and emotion | yes |
| SC-003 | Full pipeline completes under 30 min wall-clock | yes |
| SC-004 | Consent form is verifiably signed before training | yes |

## Dependencies

| Capability | Type |
|------------|------|
| process-payment | hard |
| manage-crm | optional |

## Security Classification

confidential

## LLM Fit

| Dimension | Value |
|-----------|-------|
| Complexity | high |
| Reasoning Level | high |
| Domain Specialization | domain |
